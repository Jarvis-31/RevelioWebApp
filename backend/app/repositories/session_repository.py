from datetime import datetime

from sqlalchemy import Select, and_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.time import now_utc, rome_day_bounds_utc
from app.models.enums import MachineCode, SessionStatus
from app.models.machine import Machine
from app.models.session import Session as WorkSession


class SessionRepository:

    @staticmethod
    def _get_relevant_window_start(reference_time: datetime | None = None) -> datetime:
        start_of_day, _ = rome_day_bounds_utc(reference_time)
        return start_of_day

    def get_by_id(self, db: Session, session_id: int) -> WorkSession | None:
        statement: Select[tuple[WorkSession]] = (
            select(WorkSession)
            .options(
                joinedload(WorkSession.machine),
                joinedload(WorkSession.technician),
            )
            .where(WorkSession.id == session_id)
        )
        return db.execute(statement).unique().scalar_one_or_none()

    def list_by_machine_id(self, db: Session, machine_id: int) -> list[WorkSession]:
        relevant_start = self._get_relevant_window_start()

        statement: Select[tuple[WorkSession]] = (
            select(WorkSession)
            .options(
                joinedload(WorkSession.machine),
                joinedload(WorkSession.technician),
                selectinload(WorkSession.exams),
            )
            .where(
                WorkSession.machine_id == machine_id,
                WorkSession.end_at >= relevant_start,
            )
            .order_by(WorkSession.start_at.asc())
        )
        return list(db.execute(statement).unique().scalars().all())

    def list_by_machine_code(self, db: Session, machine_code: MachineCode) -> list[WorkSession]:
        relevant_start = self._get_relevant_window_start()

        statement: Select[tuple[WorkSession]] = (
            select(WorkSession)
            .join(WorkSession.machine)
            .options(
                joinedload(WorkSession.machine),
                joinedload(WorkSession.technician),
                selectinload(WorkSession.exams),
            )
            .where(
                Machine.code == machine_code,
                WorkSession.end_at >= relevant_start,
            )
            .order_by(WorkSession.start_at.asc())
        )
        return list(db.execute(statement).unique().scalars().all())

    def get_active_for_machine(
        self,
        db: Session,
        machine_id: int,
        reference_time: datetime | None = None,
    ) -> WorkSession | None:
        current_time = reference_time or now_utc()

        statement: Select[tuple[WorkSession]] = (
            select(WorkSession)
            .options(
                joinedload(WorkSession.machine),
                joinedload(WorkSession.technician),
            )
            .where(
                and_(
                    WorkSession.machine_id == machine_id,
                    WorkSession.status == SessionStatus.ACTIVE,
                    WorkSession.start_at <= current_time,
                    WorkSession.end_at > current_time,
                )
            )
            .order_by(
                WorkSession.start_at.desc(),
                WorkSession.id.desc(),
            )
            .limit(1)
        )
        return db.execute(statement).unique().scalars().first()

    def get_active_for_technician(
        self,
        db: Session,
        technician_id: int,
        reference_time: datetime | None = None,
    ) -> WorkSession | None:
        current_time = reference_time or now_utc()

        statement: Select[tuple[WorkSession]] = (
            select(WorkSession)
            .options(
                joinedload(WorkSession.machine),
                joinedload(WorkSession.technician),
            )
            .where(
                and_(
                    WorkSession.technician_id == technician_id,
                    WorkSession.status == SessionStatus.ACTIVE,
                    WorkSession.start_at <= current_time,
                    WorkSession.end_at > current_time,
                )
            )
            .order_by(
                WorkSession.start_at.desc(),
                WorkSession.id.desc(),
            )
            .limit(1)
        )
        return db.execute(statement).unique().scalars().first()

    def list_by_technician_id(self, db: Session, technician_id: int) -> list[WorkSession]:
        relevant_start = self._get_relevant_window_start()

        statement: Select[tuple[WorkSession]] = (
            select(WorkSession)
            .options(
                joinedload(WorkSession.machine),
                joinedload(WorkSession.technician),
            )
            .where(
                WorkSession.technician_id == technician_id,
                WorkSession.end_at >= relevant_start,
            )
            .order_by(WorkSession.start_at.asc())
        )
        return list(db.execute(statement).unique().scalars().all())
