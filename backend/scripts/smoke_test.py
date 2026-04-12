from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request
from zoneinfo import ZoneInfo


HOST = "127.0.0.1"
USERNAME = "Amaggio"
PASSWORD = "Alessiom92!"
FINAL_STATUSES = {"COMPLETED", "CANCELLED"}
FSM_STATUSES = {"SCHEDULED", "ARRIVED", "IN_PROGRESS", "COMPLETED", "CANCELLED"}
ROME_TIMEZONE = ZoneInfo("Europe/Rome")


def main() -> int:
    backend_dir = Path(__file__).resolve().parents[1]
    port = find_free_port()
    db_fd, db_path = tempfile.mkstemp(prefix="revelio_smoke_", suffix=".db")
    os.close(db_fd)

    process: subprocess.Popen[str] | None = None

    try:
        process = start_server(backend_dir=backend_dir, port=port, db_path=db_path)
        wait_for_health(port=port, process=process)
        run_checks(port=port)
        print("\nSUMMARY: smoke test completato con successo.")
        return 0
    finally:
        if process is not None:
            stop_server(process)

        try:
            os.remove(db_path)
        except FileNotFoundError:
            pass


def run_checks(*, port: int) -> None:
    base = f"http://{HOST}:{port}"

    status, html = fetch(base, "/")
    check("frontend root", status == 200 and "/styles.css" in html and "/app.js" in html, f"status={status}")

    status, css = fetch(base, "/styles.css")
    check("frontend css", status == 200 and "--color-navy: #0f2340;" in css, f"status={status}")

    status, js = fetch(base, "/app.js")
    check("frontend js", status == 200 and "apiFetch" in js and "renderLogin" in js, f"status={status}")

    status, health = fetch(base, "/health", expect_json=True)
    check("health", status == 200 and health.get("status") == "ok", f"status={status}, body={health}")

    status, login = fetch(
        base,
        "/api/v1/auth/login",
        method="POST",
        data={"username": USERNAME, "password": PASSWORD},
        expect_json=True,
    )
    check("login", status == 200 and "access_token" in login, f"status={status}")

    token = login["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    status, me = fetch(base, "/api/v1/auth/me", headers=auth_headers, expect_json=True)
    check("auth me", status == 200 and me["username"] == USERNAME, f"status={status}, user={me.get('full_name')}")

    status, machines = fetch(base, "/api/v1/machines", headers=auth_headers, expect_json=True)
    check("machines", status == 200 and isinstance(machines, list) and len(machines) >= 3, f"status={status}, count={len(machines)}")

    machine_codes = [machine["code"] for machine in machines]
    for code in ("RM", "TC", "RX"):
        check(f"machine {code} present", code in machine_codes, f"codes={machine_codes}")

    worklists: dict[str, dict[str, Any]] = {}
    for code in machine_codes:
        status, worklist = fetch(base, f"/api/v1/machines/{code}/worklist", headers=auth_headers, expect_json=True)
        check(f"{code} worklist", status == 200 and worklist["machine"]["code"] == code, f"status={status}")
        check(f"{code} session count", len(worklist["sessions"]) >= 1, f"sessions={len(worklist['sessions'])}")
        for session in worklist["sessions"]:
            start_local = parse_api_datetime(session["start_at"]).astimezone(ROME_TIMEZONE)
            end_local = parse_api_datetime(session["end_at"]).astimezone(ROME_TIMEZONE)
            slot = (start_local.hour, start_local.minute, end_local.hour, end_local.minute)
            check(
                f"{code} session slot {session['id']}",
                slot in {(8, 0, 14, 0), (14, 0, 20, 0)},
                f"slot={slot}",
            )
            statuses = [exam["status"] for exam in session["exams"]]
            if session.get("is_active_now"):
                check(
                    f"{code} active fsm coverage",
                    set(statuses) == FSM_STATUSES,
                    f"statuses={sorted(set(statuses))}",
                )
            else:
                check(
                    f"{code} out-of-shift scheduled only",
                    all(status == "SCHEDULED" for status in statuses),
                    f"statuses={sorted(set(statuses))}",
                )
        worklists[code] = worklist

    candidate_exam = None
    inactive_own_exam = None
    foreign_exam = None

    for code, worklist in worklists.items():
        for session in worklist["sessions"]:
            for exam in session["exams"]:
                if exam["status"] in FINAL_STATUSES:
                    continue

                if session["technician_id"] == me["id"]:
                    if session.get("is_active_now") and candidate_exam is None:
                        candidate_exam = exam
                    if inactive_own_exam is None:
                        inactive_own_exam = exam
                elif foreign_exam is None:
                    foreign_exam = exam

    check("foreign exam found", foreign_exam is not None, f"exam={foreign_exam}")

    status, foreign_detail = fetch(
        base,
        f"/api/v1/exams/{foreign_exam['id']}",
        headers=auth_headers,
        expect_json=True,
    )
    check("foreign exam detail", status == 200 and foreign_detail["id"] == foreign_exam["id"], f"status={status}")
    check(
        "foreign allowed transitions hidden",
        len(foreign_detail["allowed_transitions"]) == 0,
        f"allowed={foreign_detail['allowed_transitions']}",
    )

    status, foreign_forbidden = fetch(
        base,
        f"/api/v1/exams/{foreign_exam['id']}/state-transitions",
        method="POST",
        headers=auth_headers,
        data={"target_status": "ARRIVED"},
        expect_json=True,
    )
    foreign_message = (
        foreign_forbidden.get("detail", "").lower()
        if isinstance(foreign_forbidden, dict)
        else str(foreign_forbidden).lower()
    )
    check(
        "foreign transition forbidden",
        status == 403 and "autorizz" in foreign_message,
        f"status={status}, body={foreign_forbidden}",
    )

    if candidate_exam is not None:
        exam_id = candidate_exam["id"]
        status, detail = fetch(base, f"/api/v1/exams/{exam_id}", headers=auth_headers, expect_json=True)
        check("exam detail", status == 200 and detail["id"] == exam_id, f"status={status}, exam_status={detail.get('status')}")
        check("allowed transitions present", len(detail["allowed_transitions"]) >= 1, f"allowed={detail['allowed_transitions']}")
        check("birth date available", bool(detail["patient"].get("birth_date")), f"birth_date={detail['patient'].get('birth_date')}")

        allowed = detail["allowed_transitions"]
        if "CANCELLED" in allowed:
            status, bad_cancel = fetch(
                base,
                f"/api/v1/exams/{exam_id}/state-transitions",
                method="POST",
                headers=auth_headers,
                data={"target_status": "CANCELLED"},
                expect_json=True,
            )
            message = bad_cancel.get("detail", "").lower() if isinstance(bad_cancel, dict) else str(bad_cancel).lower()
            check("cancel note validation", status == 400 and "nota" in message, f"status={status}, body={bad_cancel}")

        target_status = next((item for item in allowed if item != "CANCELLED"), allowed[0])
        payload: dict[str, Any] = {"target_status": target_status}
        if target_status == "CANCELLED":
            payload["note"] = "Smoke test"

        status, transitioned = fetch(
            base,
            f"/api/v1/exams/{exam_id}/state-transitions",
            method="POST",
            headers=auth_headers,
            data=payload,
            expect_json=True,
        )
        check(
            "state transition",
            status == 200 and transitioned["current_status"] == target_status,
            f"status={status}, current={transitioned.get('current_status')}",
        )

        status, updated_detail = fetch(base, f"/api/v1/exams/{exam_id}", headers=auth_headers, expect_json=True)
        check(
            "updated exam detail",
            status == 200 and updated_detail["status"] == target_status,
            f"status={status}, new_status={updated_detail.get('status')}",
        )
        check(
            "audit event persisted",
            len(updated_detail["audit_events"]) >= 1,
            f"audit_events={len(updated_detail['audit_events'])}",
        )
        return

    check("inactive own exam found", inactive_own_exam is not None, f"exam={inactive_own_exam}")

    exam_id = inactive_own_exam["id"]
    status, detail = fetch(base, f"/api/v1/exams/{exam_id}", headers=auth_headers, expect_json=True)
    check("inactive exam detail", status == 200 and detail["id"] == exam_id, f"status={status}")
    check(
        "inactive allowed transitions hidden",
        len(detail["allowed_transitions"]) == 0,
        f"allowed={detail['allowed_transitions']}",
    )

    status, blocked = fetch(
        base,
        f"/api/v1/exams/{exam_id}/state-transitions",
        method="POST",
        headers=auth_headers,
        data={"target_status": "ARRIVED"},
        expect_json=True,
    )
    blocked_message = blocked.get("detail", "").lower() if isinstance(blocked, dict) else str(blocked).lower()
    check(
        "out-of-shift transition forbidden",
        status == 403 and "fascia" in blocked_message,
        f"status={status}, body={blocked}",
    )


def fetch(
    base: str,
    path: str,
    *,
    method: str = "GET",
    data: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    expect_json: bool = False,
) -> tuple[int, Any]:
    body = None
    final_headers = {"Accept": "application/json" if expect_json else "*/*"}
    if headers:
        final_headers.update(headers)
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        final_headers["Content-Type"] = "application/json"

    req = request.Request(base + path, data=body, headers=final_headers, method=method)

    try:
        with request.urlopen(req, timeout=10) as response:
            raw = response.read()
            text = raw.decode("utf-8", errors="replace")
            if expect_json:
                return response.status, json.loads(text)
            return response.status, text
    except error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        if expect_json:
            try:
                return exc.code, json.loads(text)
            except json.JSONDecodeError:
                return exc.code, {"detail": text}
        return exc.code, text


def start_server(*, backend_dir: Path, port: int, db_path: str) -> subprocess.Popen[str]:
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_path}"

    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            HOST,
            "--port",
            str(port),
        ],
        cwd=backend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def wait_for_health(*, port: int, process: subprocess.Popen[str], timeout: float = 20.0) -> None:
    deadline = time.time() + timeout
    base = f"http://{HOST}:{port}"

    while time.time() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise RuntimeError(f"Il server si e' chiuso durante lo startup.\n{output}")

        try:
            status, body = fetch(base, "/health", expect_json=True)
            if status == 200 and body.get("status") == "ok":
                return
        except Exception:
            pass

        time.sleep(0.2)

    output = process.stdout.read() if process.stdout else ""
    raise TimeoutError(f"Timeout in attesa di /health.\n{output}")


def stop_server(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, 0))
        return int(sock.getsockname()[1])


def parse_api_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def check(name: str, condition: bool, detail: str) -> None:
    label = "OK" if condition else "FAIL"
    print(f"[{label}] {name}: {detail}")
    if not condition:
        raise SystemExit(1)


if __name__ == "__main__":
    raise SystemExit(main())
