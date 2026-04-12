from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.technician import Technician


class TechnicianRepository:

    def get_by_id(self, db: Session, technician_id: int) -> Technician | None:
        statement: Select[tuple[Technician]] = select(Technician).where(
            Technician.id == technician_id
        )
        return db.execute(statement).scalar_one_or_none()

    def get_by_username(self, db: Session, username: str) -> Technician | None:
        statement: Select[tuple[Technician]] = select(Technician).where(
            Technician.username == username
        )
        return db.execute(statement).scalar_one_or_none()

    def list_all(self, db: Session) -> list[Technician]:
        statement: Select[tuple[Technician]] = select(Technician).order_by(
            Technician.username.asc()
        )
        return list(db.execute(statement).scalars().all())
