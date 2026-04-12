from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.time import now_utc
from app.models.enums import ExamStatus
from app.models.exam import Exam
from app.models.exam_audit_event import ExamAuditEvent
from app.models.patient import Patient
from app.models.session import Session as WorkSession
from app.models.technician import Technician


class ExamRepository:

    def get_by_id(self, db: Session, exam_id: int) -> Exam | None:
        statement: Select[tuple[Exam]] = (
            select(Exam)
            .options(
                joinedload(Exam.patient),
                joinedload(Exam.session).joinedload(WorkSession.machine),
                joinedload(Exam.session).joinedload(WorkSession.technician),
            )
            .where(Exam.id == exam_id)
        )
        return db.execute(statement).unique().scalar_one_or_none()

    def get_by_id_with_audit(self, db: Session, exam_id: int) -> Exam | None:
        statement: Select[tuple[Exam]] = (
            select(Exam)
            .options(
                joinedload(Exam.patient),
                joinedload(Exam.session).joinedload(WorkSession.machine),
                joinedload(Exam.session).joinedload(WorkSession.technician),
                selectinload(Exam.audit_events).joinedload(ExamAuditEvent.performed_by),
            )
            .where(Exam.id == exam_id)
        )
        return db.execute(statement).unique().scalar_one_or_none()

    def list_by_session_id(self, db: Session, session_id: int) -> list[Exam]:
        statement: Select[tuple[Exam]] = (
            select(Exam)
            .options(
                joinedload(Exam.patient),
                joinedload(Exam.session).joinedload(WorkSession.machine),
                joinedload(Exam.session).joinedload(WorkSession.technician),
            )
            .where(Exam.session_id == session_id)
            .order_by(Exam.scheduled_time.asc(), Exam.id.asc())
        )
        return list(db.execute(statement).unique().scalars().all())

    def list_by_session_ids(self, db: Session, session_ids: list[int]) -> list[Exam]:
        if not session_ids:
            return []

        statement: Select[tuple[Exam]] = (
            select(Exam)
            .options(
                joinedload(Exam.patient),
                joinedload(Exam.session).joinedload(WorkSession.machine),
                joinedload(Exam.session).joinedload(WorkSession.technician),
            )
            .where(Exam.session_id.in_(session_ids))
            .order_by(Exam.session_id.asc(), Exam.scheduled_time.asc(), Exam.id.asc())
        )
        return list(db.execute(statement).unique().scalars().all())

    def list_by_machine_id(self, db: Session, machine_id: int) -> list[Exam]:
        statement: Select[tuple[Exam]] = (
            select(Exam)
            .join(Exam.session)
            .options(
                joinedload(Exam.patient),
                joinedload(Exam.session).joinedload(WorkSession.machine),
                joinedload(Exam.session).joinedload(WorkSession.technician),
            )
            .where(WorkSession.machine_id == machine_id)
            .order_by(Exam.session_id.asc(), Exam.scheduled_time.asc(), Exam.id.asc())
        )
        return list(db.execute(statement).unique().scalars().all())

    def update_state(
        self,
        db: Session,
        exam: Exam,
        new_status: ExamStatus,
        updated_at: datetime | None = None,
    ) -> Exam:
        timestamp = updated_at or now_utc()

        exam.status = new_status
        exam.status_updated_at = timestamp
        exam.updated_at = timestamp

        db.add(exam)
        db.flush()

        return exam

    def save(self, db: Session, exam: Exam) -> Exam:
        db.add(exam)
        db.flush()
        return exam
