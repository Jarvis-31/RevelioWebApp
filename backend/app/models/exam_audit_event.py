from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import now_utc
from app.db.session import Base
from app.models.enums import ExamStatus

if TYPE_CHECKING:
    from app.models.exam import Exam
    from app.models.technician import Technician


class ExamAuditEvent(Base):

    __tablename__ = "exam_audit_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    exam_id: Mapped[int] = mapped_column(
        ForeignKey("exams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    performed_by_technician_id: Mapped[int] = mapped_column(
        ForeignKey("technicians.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    from_status: Mapped[ExamStatus] = mapped_column(
        Enum(ExamStatus, native_enum=False),
        nullable=False,
    )
    to_status: Mapped[ExamStatus] = mapped_column(
        Enum(ExamStatus, native_enum=False),
        nullable=False,
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_utc,
        index=True,
    )
    meta: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )


    exam: Mapped["Exam"] = relationship(
        back_populates="audit_events",
    )


    performed_by: Mapped["Technician"] = relationship(
        back_populates="audit_events",
    )

    def is_cancellation(self) -> bool:
        return self.to_status == ExamStatus.CANCELLED

    def has_mandatory_note(self) -> bool:
        if self.is_cancellation():
            return bool(self.note and self.note.strip())
        return True

    def changes_state(self) -> bool:
        return self.from_status != self.to_status

    def is_consistent(self) -> bool:
        return self.changes_state() and self.has_mandatory_note()

    def __repr__(self) -> str:
        return (
            f"ExamAuditEvent(id={self.id!r}, exam_id={self.exam_id!r}, "
            f"from_status={self.from_status.value!r}, to_status={self.to_status.value!r})"
        )
