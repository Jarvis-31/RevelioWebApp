from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import now_utc
from app.db.session import Base
from app.models.enums import ExamStatus

if TYPE_CHECKING:
    from app.models.exam_audit_event import ExamAuditEvent
    from app.models.patient import Patient
    from app.models.session import Session


class Exam(Base):

    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    exam_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    scheduled_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[ExamStatus] = mapped_column(
        Enum(ExamStatus, native_enum=False),
        nullable=False,
        default=ExamStatus.SCHEDULED,
    )
    status_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_utc,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_utc,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_utc,
        onupdate=now_utc,
    )


    session: Mapped["Session"] = relationship(
        back_populates="exams",
    )


    patient: Mapped["Patient"] = relationship(
        back_populates="exams",
    )


    audit_events: Mapped[list["ExamAuditEvent"]] = relationship(
        back_populates="exam",
        cascade="save-update, merge",
        order_by="ExamAuditEvent.performed_at",
    )

    @staticmethod
    def get_allowed_transitions_from(status: ExamStatus) -> set[ExamStatus]:
        transitions: dict[ExamStatus, set[ExamStatus]] = {
            ExamStatus.SCHEDULED: {ExamStatus.ARRIVED, ExamStatus.CANCELLED},
            ExamStatus.ARRIVED: {ExamStatus.IN_PROGRESS, ExamStatus.CANCELLED},
            ExamStatus.IN_PROGRESS: {ExamStatus.COMPLETED},
            ExamStatus.COMPLETED: set(),
            ExamStatus.CANCELLED: set(),
        }
        return transitions.get(status, set())

    def get_allowed_transitions(self) -> list[ExamStatus]:
        return list(self.get_allowed_transitions_from(self.status))

    def can_transition_to(self, target: ExamStatus) -> bool:
        return target in self.get_allowed_transitions_from(self.status)

    def requires_note_for(self, target: ExamStatus) -> bool:
        return target == ExamStatus.CANCELLED

    def is_scheduled(self) -> bool:
        return self.status == ExamStatus.SCHEDULED

    def is_arrived(self) -> bool:
        return self.status == ExamStatus.ARRIVED

    def is_in_progress(self) -> bool:
        return self.status == ExamStatus.IN_PROGRESS

    def is_completed(self) -> bool:
        return self.status == ExamStatus.COMPLETED

    def is_cancelled(self) -> bool:
        return self.status == ExamStatus.CANCELLED

    def get_current_status(self) -> ExamStatus:
        return self.status

    def __repr__(self) -> str:
        return f"Exam(id={self.id!r}, exam_code={self.exam_code!r}, status={self.status.value!r})"
