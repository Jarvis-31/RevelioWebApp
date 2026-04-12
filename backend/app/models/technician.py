from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import now_utc
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.exam_audit_event import ExamAuditEvent
    from app.models.session import Session


class Technician(Base):

    __tablename__ = "technicians"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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


    sessions: Mapped[list["Session"]] = relationship(
        back_populates="technician",
        cascade="save-update, merge",
    )


    audit_events: Mapped[list["ExamAuditEvent"]] = relationship(
        back_populates="performed_by",
        cascade="save-update, merge",
    )

    def is_enabled(self) -> bool:
        return self.is_active

    def get_display_name(self) -> str:
        return self.full_name

    def __repr__(self) -> str:
        return f"Technician(id={self.id!r}, username={self.username!r})"
