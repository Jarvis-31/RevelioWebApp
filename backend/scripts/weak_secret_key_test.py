from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib import error, request

from jose import jwt


HOST = "127.0.0.1"
LOGIN_USERNAME = "Amaggio"
LOGIN_PASSWORD = "Alessiom92!"
ALGORITHM = "HS256"


class ScenarioResult:

    def __init__(
        self,
        *,
        name: str,
        server_secret: str,
        attacker_secret: str,
        own_user: str,
        own_id: int,
        target_sub: str,
        expected_status: int,
        actual_status: int,
        actual_user: str | None,
    ) -> None:
        self.name = name
        self.server_secret = server_secret
        self.attacker_secret = attacker_secret
        self.own_user = own_user
        self.own_id = own_id
        self.target_sub = target_sub
        self.expected_status = expected_status
        self.actual_status = actual_status
        self.actual_user = actual_user

    @property
    def passed(self) -> bool:
        return self.actual_status == self.expected_status


def main() -> int:
    scenario_a = run_scenario(
        name="A) Chiave forte lato server, tentativo con chiave sbagliata",
        server_secret="5f98ef6e63fa4df0f5fa416f84617b99e7795e0f44d03e5139ddf731f9de59f445bcfd7b67fcccf9952f0765742eb314",
        attacker_secret="123456",
        expected_status=401,
    )

    scenario_b = run_scenario(
        name="B) Chiave debole e prevedibile lato server",
        server_secret="123456",
        attacker_secret="123456",
        expected_status=200,
    )

    print("\n=== RISULTATO FINALE ===")
    print(format_result(scenario_a))
    print(format_result(scenario_b))

    if scenario_a.passed and scenario_b.passed:
        print("\nCONCLUSIONE: con SECRET_KEY debole/prevedibile un token falsificato puo' essere accettato.")
        return 0

    print("\nCONCLUSIONE: test non coerente con le attese, controllare l'ambiente.")
    return 1


def run_scenario(
    *,
    name: str,
    server_secret: str,
    attacker_secret: str,
    expected_status: int,
) -> ScenarioResult:
    backend_dir = Path(__file__).resolve().parents[1]
    port = find_free_port()

    db_fd, db_path = tempfile.mkstemp(prefix="revelio_weak_secret_", suffix=".db")
    os.close(db_fd)

    process: subprocess.Popen[str] | None = None

    try:
        process = start_server(
            backend_dir=backend_dir,
            port=port,
            db_path=db_path,
            server_secret=server_secret,
        )
        wait_for_health(port=port, process=process)

        base = f"http://{HOST}:{port}"

        login_status, login_data = fetch(
            base,
            "/api/v1/auth/login",
            method="POST",
            data={"username": LOGIN_USERNAME, "password": LOGIN_PASSWORD},
            expect_json=True,
        )
        require(login_status == 200, f"Login fallito nello scenario '{name}'")

        own_id = int(login_data["technician"]["id"])
        own_user = str(login_data["technician"]["username"])
        legit_token = str(login_data["access_token"])

        target_sub = find_other_technician_id(base=base, token=legit_token, own_id=own_id)

        forged_token = build_forged_token(
            signing_secret=attacker_secret,
            subject=target_sub,
        )

        forged_status, forged_body = fetch(
            base,
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {forged_token}"},
            expect_json=True,
        )

        forged_user = None
        if isinstance(forged_body, dict) and forged_status == 200:
            forged_user = forged_body.get("username")

        print(f"\n{name}")
        print(f"- SECRET_KEY server: {server_secret}")
        print(f"- SECRET usata dall'attaccante: {attacker_secret}")
        print(f"- Utente reale login: {own_user} (id={own_id})")
        print(f"- sub target nel token forged: {target_sub}")
        print(f"- HTTP atteso: {expected_status}")
        print(f"- HTTP ottenuto: {forged_status}")
        if forged_user is not None:
            print(f"- Utente risolto da /auth/me: {forged_user}")

        return ScenarioResult(
            name=name,
            server_secret=server_secret,
            attacker_secret=attacker_secret,
            own_user=own_user,
            own_id=own_id,
            target_sub=target_sub,
            expected_status=expected_status,
            actual_status=forged_status,
            actual_user=forged_user,
        )
    finally:
        if process is not None:
            stop_server(process)
        try:
            os.remove(db_path)
        except FileNotFoundError:
            pass


def find_other_technician_id(*, base: str, token: str, own_id: int) -> str:
    status, machines = fetch(
        base,
        "/api/v1/machines",
        headers={"Authorization": f"Bearer {token}"},
        expect_json=True,
    )
    require(status == 200, "Impossibile leggere le macchine.")

    technician_ids: set[int] = set()
    for machine in machines:
        code = machine["code"]
        st, worklist = fetch(
            base,
            f"/api/v1/machines/{code}/worklist",
            headers={"Authorization": f"Bearer {token}"},
            expect_json=True,
        )
        require(st == 200, f"Worklist non disponibile per {code}.")
        for session in worklist["sessions"]:
            technician_ids.add(int(session["technician_id"]))

    for technician_id in sorted(technician_ids):
        if technician_id != own_id:
            return str(technician_id)

    return str(own_id)


def build_forged_token(*, signing_secret: str, subject: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=15)).timestamp()),
    }
    return jwt.encode(payload, signing_secret, algorithm=ALGORITHM)


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
            raw = response.read().decode("utf-8", errors="replace")
            if expect_json:
                return response.status, json.loads(raw)
            return response.status, raw
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        if expect_json:
            try:
                return exc.code, json.loads(raw)
            except json.JSONDecodeError:
                return exc.code, {"detail": raw}
        return exc.code, raw


def start_server(
    *,
    backend_dir: Path,
    port: int,
    db_path: str,
    server_secret: str,
) -> subprocess.Popen[str]:
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_path}"
    env["SECRET_KEY"] = server_secret
    env["ALGORITHM"] = ALGORITHM
    env["DEBUG"] = "false"

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
            raise RuntimeError(f"Server terminato in startup.\n{output}")

        try:
            status, body = fetch(base, "/health", expect_json=True)
            if status == 200 and body.get("status") == "ok":
                return
        except Exception:
            pass

        time.sleep(0.2)

    output = process.stdout.read() if process.stdout else ""
    raise TimeoutError(f"Timeout su /health.\n{output}")


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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def format_result(result: ScenarioResult) -> str:
    mark = "PASS" if result.passed else "FAIL"
    return (
        f"[{mark}] {result.name}: atteso={result.expected_status}, "
        f"ottenuto={result.actual_status}, target_sub={result.target_sub}, "
        f"utente_risolto={result.actual_user}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
