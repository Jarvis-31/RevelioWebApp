from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.core.time import now_utc
from app.models.enums import MachineCode
from app.repositories.exam_repository import ExamRepository
from app.repositories.machine_repository import MachineRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.machine import (
    MachineResponse,
    MachineWorklistResponse,
    WorklistExamResponse,
    WorklistPatientResponse,
    WorklistSessionResponse,
)


class WorklistService:

    def __init__(self) -> None:
        self.machine_repository = MachineRepository()
        self.session_repository = SessionRepository()
        self.exam_repository = ExamRepository()

    def list_machines(self, db: Session) -> list[MachineResponse]:
        machines = self.machine_repository.list_active(db)
        return [MachineResponse.model_validate(machine) for machine in machines]

    def get_machine_worklist(
        self,
        db: Session,
        *,
        machine_code: MachineCode,
    ) -> MachineWorklistResponse:
        machine = self.machine_repository.get_by_code(db, machine_code)
        if machine is None:
            raise ResourceNotFoundError("Macchina non trovata.")

        generated_at = now_utc()

        sessions = self.session_repository.list_by_machine_code(db, machine_code)
        active_session = self.session_repository.get_active_for_machine(
            db,
            machine.id,
            reference_time=generated_at,
        )

        session_ids = [session.id for session in sessions]
        exams = self.exam_repository.list_by_session_ids(db, session_ids)

        exams_by_session_id = defaultdict(list)
        for exam in exams:
            exams_by_session_id[exam.session_id].append(exam)

        session_responses: list[WorklistSessionResponse] = []

        for session in sessions:
            worklist_exams = [
                WorklistExamResponse(
                    id=exam.id,
                    exam_code=exam.exam_code,
                    scheduled_time=exam.scheduled_time,
                    status=exam.status,
                    session_id=exam.session_id,
                    patient=WorklistPatientResponse(
                        id=exam.patient.id,
                        patient_code=exam.patient.patient_code,
                        first_name=exam.patient.first_name,
                        last_name=exam.patient.last_name,
                    ),
                )
                for exam in exams_by_session_id.get(session.id, [])
            ]

            session_responses.append(
                WorklistSessionResponse(
                    id=session.id,
                    start_at=session.start_at,
                    end_at=session.end_at,
                    status=session.status,
                    technician_id=session.technician.id,
                    technician_name=session.technician.full_name,
                    is_active_now=active_session is not None and active_session.id == session.id,
                    exams=worklist_exams,
                )
            )

        return MachineWorklistResponse(
            machine=MachineResponse.model_validate(machine),
            generated_at=generated_at,
            active_session_id=active_session.id if active_session is not None else None,
            sessions=session_responses,
        )
