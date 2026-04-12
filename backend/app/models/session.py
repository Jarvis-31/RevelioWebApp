from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import now_utc
from app.db.session import Base
from app.models.enums import SessionStatus

if TYPE_CHECKING:
    from app.models.exam import Exam
    from app.models.machine import Machine
    from app.models.technician import Technician


class Session(Base):

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    machine_id: Mapped[int] = mapped_column(
        ForeignKey("machines.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    technician_id: Mapped[int] = mapped_column(
        ForeignKey("technicians.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, native_enum=False),
        nullable=False,
        default=SessionStatus.PLANNED,
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


    machine: Mapped["Machine"] = relationship(
        back_populates="sessions",
    )


    technician: Mapped["Technician"] = relationship(
        back_populates="sessions",
    )


    exams: Mapped[list["Exam"]] = relationship(
        back_populates="session",
        cascade="save-update, merge",
    )

    def is_active(self) -> bool:
        return self.status == SessionStatus.ACTIVE

    def is_planned(self) -> bool:
        return self.status == SessionStatus.PLANNED

    def is_closed(self) -> bool:
        return self.status == SessionStatus.CLOSED

    def belongs_to(self, technician_id: int) -> bool:
        return self.technician_id == technician_id

    def __repr__(self) -> str:
        return (
            f"Session(id={self.id!r}, machine_id={self.machine_id!r}, "
            f"technician_id={self.technician_id!r}, status={self.status.value!r})"
        )
