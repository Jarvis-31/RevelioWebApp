from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.machine import Machine
from app.models.enums import MachineCode


class MachineRepository:

    def get_by_id(self, db: Session, machine_id: int) -> Machine | None:
        statement: Select[tuple[Machine]] = select(Machine).where(
            Machine.id == machine_id
        )
        return db.execute(statement).scalar_one_or_none()

    def get_by_code(self, db: Session, code: MachineCode) -> Machine | None:
        statement: Select[tuple[Machine]] = select(Machine).where(
            Machine.code == code
        )
        return db.execute(statement).scalar_one_or_none()

    def list_all(self, db: Session) -> list[Machine]:
        statement: Select[tuple[Machine]] = select(Machine).order_by(Machine.code.asc())
        return list(db.execute(statement).scalars().all())

    def list_active(self, db: Session) -> list[Machine]:
        statement: Select[tuple[Machine]] = (
            select(Machine)
            .where(Machine.is_active.is_(True))
            .order_by(Machine.code.asc())
        )
        return list(db.execute(statement).scalars().all())
