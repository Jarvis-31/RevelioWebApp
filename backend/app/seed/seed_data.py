from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import Select, delete, select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.core.time import now_rome, now_utc, rome_shift_window_utc
from app.models.enums import ExamStatus, MachineCode, SessionStatus
from app.models.exam import Exam
from app.models.exam_audit_event import ExamAuditEvent
from app.models.machine import Machine
from app.models.patient import Patient
from app.models.session import Session as WorkSession
from app.models.technician import Technician


LOGIN_TECHNICIAN_USERNAME = "Amaggio"
LOGIN_TECHNICIAN_PASSWORD = "Alessiom92!"
DEFAULT_TECHNICIAN_PASSWORD = LOGIN_TECHNICIAN_PASSWORD

TECHNICIAN_DEFINITIONS = [
    {
        "username": "Amaggio",
        "full_name": "Alessio Maggio",
        "password": "Alessiom92!",
        "legacy_usernames": ["michelemassignan", "tecnico.rm"],
        "is_active": True,
    },
    {
        "username": "Rmaselli",
        "full_name": "Roberto Maselli",
        "password": "Robertom79!",
        "legacy_usernames": ["elenamoretti", "tecnico.tc"],
        "is_active": True,
    },
    {
        "username": "Edipiero",
        "full_name": "Erika Di Piero",
        "password": "Erikad98!",
        "legacy_usernames": ["andreaferrari", "tecnico.rx"],
        "is_active": True,
    },
]

TECHNICIAN_USERNAME_BY_MACHINE = {
    MachineCode.RM: "Amaggio",
    MachineCode.TC: "Rmaselli",
    MachineCode.RX: "Edipiero",
}

PATIENT_DEFINITIONS = [
    {
        "patient_code": "PAT-001",
        "first_name": "Anna",
        "last_name": "Ricci",
        "birth_date": "1985-07-12",
        "sex": "F",
    },
    {
        "patient_code": "PAT-002",
        "first_name": "Marco",
        "last_name": "De Santis",
        "birth_date": "1979-03-22",
        "sex": "M",
    },
    {
        "patient_code": "PAT-003",
        "first_name": "Laura",
        "last_name": "Fontana",
        "birth_date": "1991-11-05",
        "sex": "F",
    },
    {
        "patient_code": "PAT-004",
        "first_name": "Paolo",
        "last_name": "Marini",
        "birth_date": "1968-09-17",
        "sex": "M",
    },
    {
        "patient_code": "PAT-005",
        "first_name": "Elena",
        "last_name": "Greco",
        "birth_date": "1988-01-30",
        "sex": "F",
    },
    {
        "patient_code": "PAT-006",
        "first_name": "Simone",
        "last_name": "Conti",
        "birth_date": "1994-06-14",
        "sex": "M",
    },
    {
        "patient_code": "PAT-007",
        "first_name": "Chiara",
        "last_name": "Leone",
        "birth_date": "1976-04-02",
        "sex": "F",
    },
    {
        "patient_code": "PAT-008",
        "first_name": "Davide",
        "last_name": "Serra",
        "birth_date": "1982-12-19",
        "sex": "M",
    },
    {
        "patient_code": "PAT-009",
        "first_name": "Martina",
        "last_name": "Bellini",
        "birth_date": "1997-08-25",
        "sex": "F",
    },
    {
        "patient_code": "PAT-010",
        "first_name": "Giorgio",
        "last_name": "Villa",
        "birth_date": "1973-02-08",
        "sex": "M",
    },
    {
        "patient_code": "PAT-011",
        "first_name": "Silvia",
        "last_name": "Neri",
        "birth_date": "1990-05-27",
        "sex": "F",
    },
    {
        "patient_code": "PAT-012",
        "first_name": "Roberto",
        "last_name": "Pellegrini",
        "birth_date": "1965-10-11",
        "sex": "M",
    },
    {
        "patient_code": "PAT-013",
        "first_name": "Francesca",
        "last_name": "Gentile",
        "birth_date": "1983-02-14",
        "sex": "F",
    },
    {
        "patient_code": "PAT-014",
        "first_name": "Luca",
        "last_name": "Bianchi",
        "birth_date": "1975-12-03",
        "sex": "M",
    },
    {
        "patient_code": "PAT-015",
        "first_name": "Serena",
        "last_name": "Rizzi",
        "birth_date": "1992-09-09",
        "sex": "F",
    },
]

MACHINE_SHIFT_BLUEPRINTS = {
    MachineCode.RM: {
        "slot": "AM",
        "start_hour": 8,
        "end_hour": 14,
        "exams": [
            {"suffix": "001", "offset_minutes": 20, "patient_code": "PAT-001", "status": ExamStatus.SCHEDULED},
            {"suffix": "002", "offset_minutes": 70, "patient_code": "PAT-002", "status": ExamStatus.ARRIVED},
            {"suffix": "003", "offset_minutes": 140, "patient_code": "PAT-003", "status": ExamStatus.IN_PROGRESS},
            {"suffix": "004", "offset_minutes": 200, "patient_code": "PAT-004", "status": ExamStatus.COMPLETED},
            {
                "suffix": "005",
                "offset_minutes": 250,
                "patient_code": "PAT-005",
                "status": ExamStatus.CANCELLED,
                "cancel_note": "Paziente ha rinviato l'esame per indisposizione.",
            },
        ],
    },
    MachineCode.TC: {
        "slot": "PM",
        "start_hour": 14,
        "end_hour": 20,
        "exams": [
            {"suffix": "001", "offset_minutes": 20, "patient_code": "PAT-006", "status": ExamStatus.SCHEDULED},
            {"suffix": "002", "offset_minutes": 80, "patient_code": "PAT-007", "status": ExamStatus.ARRIVED},
            {"suffix": "003", "offset_minutes": 150, "patient_code": "PAT-008", "status": ExamStatus.IN_PROGRESS},
            {"suffix": "004", "offset_minutes": 210, "patient_code": "PAT-009", "status": ExamStatus.COMPLETED},
            {
                "suffix": "005",
                "offset_minutes": 270,
                "patient_code": "PAT-010",
                "status": ExamStatus.CANCELLED,
                "cancel_note": "Esame annullato dal medico referente.",
            },
        ],
    },
    MachineCode.RX: {
        "slot": "AM",
        "start_hour": 8,
        "end_hour": 14,
        "exams": [
            {"suffix": "001", "offset_minutes": 18, "patient_code": "PAT-011", "status": ExamStatus.SCHEDULED},
            {"suffix": "002", "offset_minutes": 70, "patient_code": "PAT-012", "status": ExamStatus.ARRIVED},
            {"suffix": "003", "offset_minutes": 135, "patient_code": "PAT-013", "status": ExamStatus.IN_PROGRESS},
            {"suffix": "004", "offset_minutes": 195, "patient_code": "PAT-014", "status": ExamStatus.COMPLETED},
            {
                "suffix": "005",
                "offset_minutes": 240,
                "patient_code": "PAT-015",
                "status": ExamStatus.CANCELLED,
                "cancel_note": "Paziente non si e' presentato al check-in.",
            },
        ],
    },
}


def seed_database(db: Session) -> None:
    try:
        technicians = _seed_technicians(db)
        machines = _seed_machines(db)
        patients = _seed_patients(db)
        sessions = _seed_sessions(db, technicians=technicians, machines=machines)
        _seed_exams_and_audit(
            db,
            technicians=technicians,
            patients=patients,
            sessions=sessions,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise


def _seed_technicians(db: Session) -> dict[str, Technician]:
    technicians: dict[str, Technician] = {}

    for item in TECHNICIAN_DEFINITIONS:
        existing = _get_technician_by_username(db, item["username"])
        if existing is None:
            existing = _get_technician_by_usernames(db, item["legacy_usernames"])

        password = item.get("password") or DEFAULT_TECHNICIAN_PASSWORD

        if existing is None:
            existing = Technician(
                username=item["username"],
                password_hash=get_password_hash(password),
                full_name=item["full_name"],
                is_active=item["is_active"],
            )
            db.add(existing)
        else:
            existing.username = item["username"]
            existing.password_hash = get_password_hash(password)
            existing.full_name = item["full_name"]
            existing.is_active = item["is_active"]

        db.flush()
        technicians[item["username"]] = existing

    return technicians


def _seed_machines(db: Session) -> dict[MachineCode, Machine]:
    definitions = [
        {
            "code": MachineCode.RM,
            "display_name": "Risonanza Magnetica",
            "is_active": True,
        },
        {
            "code": MachineCode.TC,
            "display_name": "Tomografia Computerizzata",
            "is_active": True,
        },
        {
            "code": MachineCode.RX,
            "display_name": "Radiologia Tradizionale",
            "is_active": True,
        },
    ]

    machines: dict[MachineCode, Machine] = {}

    for item in definitions:
        existing = _get_machine_by_code(db, item["code"])
        if existing is None:
            existing = Machine(
                code=item["code"],
                display_name=item["display_name"],
                is_active=item["is_active"],
            )
            db.add(existing)
        else:
            existing.display_name = item["display_name"]
            existing.is_active = item["is_active"]

        db.flush()
        machines[item["code"]] = existing

    return machines


def _seed_patients(db: Session) -> dict[str, Patient]:
    patients: dict[str, Patient] = {}

    for item in PATIENT_DEFINITIONS:
        existing = _get_patient_by_code(db, item["patient_code"])

        if existing is None:
            existing = Patient(
                patient_code=item["patient_code"],
                first_name=item["first_name"],
                last_name=item["last_name"],
                birth_date=_normalize_birth_date(item["birth_date"]),
                sex=item["sex"],
            )
            db.add(existing)
        else:
            existing.first_name = item["first_name"]
            existing.last_name = item["last_name"]
            existing.birth_date = _normalize_birth_date(item["birth_date"])
            existing.sex = item["sex"]

        db.flush()
        patients[item["patient_code"]] = existing

    return patients


def _normalize_birth_date(value: date | str | None) -> date | None:
    if value is None or isinstance(value, date):
        return value

    return date.fromisoformat(value)


def _seed_sessions(
    db: Session,
    *,
    technicians: dict[str, Technician],
    machines: dict[MachineCode, Machine],
) -> dict[str, WorkSession]:
    reference_time = now_utc()
    local_day = now_rome().date()
    sessions: dict[str, WorkSession] = {}

    for machine_code, username in TECHNICIAN_USERNAME_BY_MACHINE.items():
        blueprint = MACHINE_SHIFT_BLUEPRINTS[machine_code]
        key = f"{machine_code.value.lower()}_{blueprint['slot'].lower()}"
        start_at, end_at = rome_shift_window_utc(
            local_day,
            blueprint["start_hour"],
            blueprint["end_hour"],
        )
        technician_id = technicians[username].id
        status = _resolve_session_status(
            start_at=start_at,
            end_at=end_at,
            reference_time=reference_time,
        )


        existing: WorkSession | None = None
        for session in _list_sessions_by_machine(
            db,
            machine_id=machines[machine_code].id,
        ):
            is_target_session = (
                session.technician_id == technician_id
                and session.start_at == start_at
                and session.end_at == end_at
            )
            if is_target_session:
                existing = session
                continue
            _delete_session_tree(db, session_id=session.id)

        if existing is None:
            existing = WorkSession(
                machine_id=machines[machine_code].id,
                technician_id=technician_id,
                start_at=start_at,
                end_at=end_at,
                status=status,
            )
            db.add(existing)
        else:
            existing.machine_id = machines[machine_code].id
            existing.technician_id = technician_id
            existing.start_at = start_at
            existing.end_at = end_at
            existing.status = status

        db.flush()
        sessions[key] = existing

    return sessions


def _resolve_session_status(
    *,
    start_at: datetime,
    end_at: datetime,
    reference_time: datetime,
) -> SessionStatus:
    if start_at <= reference_time < end_at:
        return SessionStatus.ACTIVE
    if reference_time < start_at:
        return SessionStatus.PLANNED
    return SessionStatus.CLOSED


def _seed_exams_and_audit(
    db: Session,
    *,
    technicians: dict[str, Technician],
    patients: dict[str, Patient],
    sessions: dict[str, WorkSession],
) -> None:
    for machine_code, username in TECHNICIAN_USERNAME_BY_MACHINE.items():
        technician = technicians[username]
        blueprint = MACHINE_SHIFT_BLUEPRINTS[machine_code]
        session_key = f"{machine_code.value.lower()}_{blueprint['slot'].lower()}"
        session = sessions[session_key]
        session_is_active = session.status == SessionStatus.ACTIVE

        for exam_blueprint in blueprint["exams"]:
            scheduled_time = session.start_at + timedelta(minutes=exam_blueprint["offset_minutes"])
            status = exam_blueprint["status"] if session_is_active else ExamStatus.SCHEDULED
            audit_events = _build_audit_events(
                status=status,
                scheduled_time=scheduled_time,
                cancel_note=exam_blueprint.get("cancel_note"),
            )
            status_updated_at = audit_events[-1]["performed_at"] if audit_events else scheduled_time
            exam_code = f"{machine_code.value}-{blueprint['slot']}-{exam_blueprint['suffix']}"
            patient = patients[exam_blueprint["patient_code"]]

            exam = _get_exam_by_code(db, exam_code)
            if exam is None:
                exam = Exam(
                    exam_code=exam_code,
                    session_id=session.id,
                    patient_id=patient.id,
                    scheduled_time=scheduled_time,
                    status=status,
                    status_updated_at=status_updated_at,
                )
                db.add(exam)
                db.flush()
            else:
                exam.session_id = session.id
                exam.patient_id = patient.id
                exam.scheduled_time = scheduled_time
                exam.status = status
                exam.status_updated_at = status_updated_at
                db.flush()

            _replace_audit_chain_for_exam(
                db,
                exam=exam,
                performed_by=technician,
                audit_events=audit_events,
            )


def _build_audit_events(
    *,
    status: ExamStatus,
    scheduled_time: datetime,
    cancel_note: str | None = None,
) -> list[dict[str, Any]]:
    arrival_at = scheduled_time - timedelta(minutes=12)
    in_progress_at = scheduled_time + timedelta(minutes=6)
    completed_at = scheduled_time + timedelta(minutes=28)
    cancelled_at = scheduled_time - timedelta(minutes=4)

    if status == ExamStatus.SCHEDULED:
        return []

    if status == ExamStatus.ARRIVED:
        return [
            {
                "from_status": ExamStatus.SCHEDULED,
                "to_status": ExamStatus.ARRIVED,
                "note": None,
                "performed_at": arrival_at,
            }
        ]

    if status == ExamStatus.IN_PROGRESS:
        return [
            {
                "from_status": ExamStatus.SCHEDULED,
                "to_status": ExamStatus.ARRIVED,
                "note": None,
                "performed_at": arrival_at,
            },
            {
                "from_status": ExamStatus.ARRIVED,
                "to_status": ExamStatus.IN_PROGRESS,
                "note": None,
                "performed_at": in_progress_at,
            },
        ]

    if status == ExamStatus.COMPLETED:
        return [
            {
                "from_status": ExamStatus.SCHEDULED,
                "to_status": ExamStatus.ARRIVED,
                "note": None,
                "performed_at": arrival_at,
            },
            {
                "from_status": ExamStatus.ARRIVED,
                "to_status": ExamStatus.IN_PROGRESS,
                "note": None,
                "performed_at": in_progress_at,
            },
            {
                "from_status": ExamStatus.IN_PROGRESS,
                "to_status": ExamStatus.COMPLETED,
                "note": None,
                "performed_at": completed_at,
            },
        ]

    return [
        {
            "from_status": ExamStatus.SCHEDULED,
            "to_status": ExamStatus.CANCELLED,
            "note": cancel_note or "Paziente non disponibile per la sessione.",
            "performed_at": cancelled_at,
        }
    ]


def _replace_audit_chain_for_exam(
    db: Session,
    *,
    exam: Exam,
    performed_by: Technician,
    audit_events: list[dict[str, Any]],
) -> None:
    db.execute(delete(ExamAuditEvent).where(ExamAuditEvent.exam_id == exam.id))
    db.flush()

    for item in audit_events:
        event = ExamAuditEvent(
            exam_id=exam.id,
            performed_by_technician_id=performed_by.id,
            from_status=item["from_status"],
            to_status=item["to_status"],
            note=item["note"],
            performed_at=item["performed_at"],
            meta={"seeded": True},
        )
        db.add(event)

    db.flush()


def _get_technician_by_username(db: Session, username: str) -> Technician | None:
    statement: Select[tuple[Technician]] = select(Technician).where(
        Technician.username == username
    )
    return db.execute(statement).scalar_one_or_none()


def _get_technician_by_usernames(db: Session, usernames: list[str]) -> Technician | None:
    if not usernames:
        return None

    statement: Select[tuple[Technician]] = select(Technician).where(
        Technician.username.in_(usernames)
    )
    return db.execute(statement).scalar_one_or_none()


def _get_machine_by_code(db: Session, code: MachineCode) -> Machine | None:
    statement: Select[tuple[Machine]] = select(Machine).where(Machine.code == code)
    return db.execute(statement).scalar_one_or_none()


def _get_patient_by_code(db: Session, patient_code: str) -> Patient | None:
    statement: Select[tuple[Patient]] = select(Patient).where(
        Patient.patient_code == patient_code
    )
    return db.execute(statement).scalar_one_or_none()


def _list_sessions_by_machine(db: Session, *, machine_id: int) -> list[WorkSession]:
    statement: Select[tuple[WorkSession]] = select(WorkSession).where(
        WorkSession.machine_id == machine_id
    )
    return list(db.execute(statement).scalars().all())


def _delete_session_tree(db: Session, *, session_id: int) -> None:
    exam_ids = list(
        db.execute(
            select(Exam.id).where(Exam.session_id == session_id)
        ).scalars().all()
    )

    if exam_ids:
        db.execute(
            delete(ExamAuditEvent).where(ExamAuditEvent.exam_id.in_(exam_ids))
        )
        db.execute(
            delete(Exam).where(Exam.id.in_(exam_ids))
        )

    db.execute(delete(WorkSession).where(WorkSession.id == session_id))
    db.flush()


def _get_exam_by_code(db: Session, exam_code: str) -> Exam | None:
    statement: Select[tuple[Exam]] = select(Exam).where(Exam.exam_code == exam_code)
    return db.execute(statement).scalar_one_or_none()
