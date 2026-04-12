from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import now_utc
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.exam import Exam


class Patient(Base):

    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    patient_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    birth_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    sex: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_utc,
    )


    exams: Mapped[list["Exam"]] = relationship(
        back_populates="patient",
        cascade="save-update, merge",
    )

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_display_identity(self) -> str:
        return f"{self.patient_code} - {self.get_full_name()}"

    def has_birth_date(self) -> bool:
        return self.birth_date is not None

    def __repr__(self) -> str:
        return f"Patient(id={self.id!r}, patient_code={self.patient_code!r})"
