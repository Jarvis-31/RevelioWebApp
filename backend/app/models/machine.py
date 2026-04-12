from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import MachineCode

if TYPE_CHECKING:
    from app.models.session import Session


class Machine(Base):

    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    code: Mapped[MachineCode] = mapped_column(
        Enum(MachineCode, native_enum=False),
        unique=True,
        index=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


    sessions: Mapped[list["Session"]] = relationship(
        back_populates="machine",
        cascade="save-update, merge",
    )

    def is_selectable(self) -> bool:
        return self.is_active

    def get_code_label(self) -> str:
        return self.code.value

    def __repr__(self) -> str:
        return f"Machine(id={self.id!r}, code={self.code.value!r})"
