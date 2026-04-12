from datetime import datetime
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.core.time import now_utc
from app.models.enums import ExamStatus
from app.models.exam_audit_event import ExamAuditEvent


class AuditRepository:

    def create(
        self,
        db: Session,
        *,
        exam_id: int,
        performed_by_technician_id: int,
        from_status: ExamStatus,
        to_status: ExamStatus,
        note: str | None = None,
        meta: dict[str, Any] | None = None,
        performed_at: datetime | None = None,
    ) -> ExamAuditEvent:
        event = ExamAuditEvent(
            exam_id=exam_id,
            performed_by_technician_id=performed_by_technician_id,
            from_status=from_status,
            to_status=to_status,
            note=note,
            meta=meta,
            performed_at=performed_at or now_utc(),
        )

        db.add(event)
        db.flush()

        return event

    def get_by_id(self, db: Session, audit_event_id: int) -> ExamAuditEvent | None:
        statement: Select[tuple[ExamAuditEvent]] = (
            select(ExamAuditEvent)
            .options(joinedload(ExamAuditEvent.performed_by))
            .where(ExamAuditEvent.id == audit_event_id)
        )
        return db.execute(statement).unique().scalar_one_or_none()

    def list_by_exam_id(self, db: Session, exam_id: int) -> list[ExamAuditEvent]:
        statement: Select[tuple[ExamAuditEvent]] = (
            select(ExamAuditEvent)
            .options(joinedload(ExamAuditEvent.performed_by))
            .where(ExamAuditEvent.exam_id == exam_id)
            .order_by(ExamAuditEvent.performed_at.asc(), ExamAuditEvent.id.asc())
        )
        return list(db.execute(statement).unique().scalars().all())
