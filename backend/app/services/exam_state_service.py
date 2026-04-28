from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthorizationError,
    InvalidStateTransitionError,
    MissingCancellationNoteError,
    ResourceNotFoundError,
)
from app.core.time import now_utc
from app.models.enums import ExamStatus
from app.models.exam import Exam
from app.models.technician import Technician
from app.models.exam_audit_event import ExamAuditEvent
from app.repositories.audit_repository import AuditRepository
from app.repositories.exam_repository import ExamRepository
from app.schemas.audit import AuditEventDetailedResponse, AuditPerformedByResponse
from app.schemas.exam import (
    ExamDetailResponse,
    ExamMachineResponse,
    ExamPatientResponse,
    ExamSessionResponse,
    ExamStateTransitionResponse,
)


class ExamStateService:

    def __init__(self) -> None:
        self.exam_repository = ExamRepository()
        self.audit_repository = AuditRepository()

    def get_exam_detail(
        self,
        db: Session,
        *,
        exam_id: int,
        current_technician: Technician,
    ) -> ExamDetailResponse:
        exam = self.exam_repository.get_by_id_with_audit(db, exam_id)
        if exam is None:
            raise ResourceNotFoundError("Esame non trovato.")

        return self._build_exam_detail_response(
            exam,
            current_technician=current_technician,
        )

    def list_audit_events(
        self,
        db: Session,
        *,
        exam_id: int,
    ) -> list[AuditEventDetailedResponse]:
        exam = self.exam_repository.get_by_id_with_audit(db, exam_id)
        if exam is None:
            raise ResourceNotFoundError("Esame non trovato.")

        return [
            self._build_audit_event_response(event)
            for event in exam.audit_events
        ]

    def request_state_change(
        self,
        db: Session,
        *,
        exam_id: int,
        target_status: ExamStatus,
        current_technician: Technician,
        note: str | None,
    ) -> ExamStateTransitionResponse:
        exam = self.exam_repository.get_by_id(db, exam_id)
        if exam is None:
            raise ResourceNotFoundError("Esame non trovato.")

        self._check_authorization(exam, current_technician)
        self._validate_transition(exam, target_status)
        self._validate_mandatory_note(target_status, note)

        previous_status = exam.status
        transition_timestamp = now_utc()

        try:
            self.exam_repository.update_state(
                db,
                exam,
                new_status=target_status,
                updated_at=transition_timestamp,
            )

            audit_event = self.audit_repository.create(
                db,
                exam_id=exam.id,
                performed_by_technician_id=current_technician.id,
                from_status=previous_status,
                to_status=target_status,
                note=note,
                meta={
                    "source": "api",
                    "seeded": False,
                    "action": "state_transition",
                },
                performed_at=transition_timestamp,
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        updated_exam = self.exam_repository.get_by_id_with_audit(db, exam.id)
        if updated_exam is None:
            raise ResourceNotFoundError("Esame aggiornato non trovato.")

        persisted_audit_event = self.audit_repository.get_by_id(db, audit_event.id)
        if persisted_audit_event is None:
            raise ResourceNotFoundError("Audit event creato non trovato.")

        return ExamStateTransitionResponse(
            exam_id=updated_exam.id,
            exam_code=updated_exam.exam_code,
            previous_status=previous_status,
            current_status=updated_exam.status,
            status_updated_at=updated_exam.status_updated_at,
            note=note,
            allowed_next_transitions=updated_exam.get_allowed_transitions(),
            audit_event=self._build_audit_event_response(persisted_audit_event),
        )

    def _check_authorization(self, exam: Exam, technician: Technician) -> None:
        if exam.session.technician_id != technician.id:
            raise AuthorizationError(
                "Non autorizzato: l'esame non appartiene alla sessione del tecnico corrente."
            )

        if not self._is_within_session_window(exam):
            raise AuthorizationError(
                "Non autorizzato: puoi cambiare stato solo durante la fascia oraria della sessione assegnata."
            )

    def _validate_transition(self, exam: Exam, target_status: ExamStatus) -> None:
        if not exam.can_transition_to(target_status):
            raise InvalidStateTransitionError("Transizione non valida per lo stato corrente.")

    def _validate_mandatory_note(
        self,
        target_status: ExamStatus,
        note: str | None,
    ) -> None:
        if target_status == ExamStatus.CANCELLED and not (note and note.strip()):
            raise MissingCancellationNoteError("Nota obbligatoria per CANCELLED.")

    def _build_exam_detail_response(
        self,
        exam: Exam,
        *,
        current_technician: Technician,
    ) -> ExamDetailResponse:
        can_manage_state = (
            exam.session.technician_id == current_technician.id
            and self._is_within_session_window(exam)
        )

        return ExamDetailResponse(
            id=exam.id,
            exam_code=exam.exam_code,
            scheduled_time=exam.scheduled_time,
            status=exam.status,
            status_updated_at=exam.status_updated_at,
            allowed_transitions=exam.get_allowed_transitions() if can_manage_state else [],
            patient=ExamPatientResponse(
                id=exam.patient.id,
                patient_code=exam.patient.patient_code,
                first_name=exam.patient.first_name,
                last_name=exam.patient.last_name,
                birth_date=exam.patient.birth_date,
                sex=exam.patient.sex,
            ),
            session=ExamSessionResponse(
                id=exam.session.id,
                start_at=exam.session.start_at,
                end_at=exam.session.end_at,
                status=exam.session.status,
                technician_id=exam.session.technician.id,
                technician_name=exam.session.technician.full_name,
                machine=ExamMachineResponse(
                    id=exam.session.machine.id,
                    code=exam.session.machine.code,
                    display_name=exam.session.machine.display_name,
                ),
            ),
            audit_events=[
                self._build_audit_event_response(event)
                for event in exam.audit_events
            ],
        )

    @staticmethod
    def _to_utc_aware(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    def _is_within_session_window(
        self,
        exam: Exam,
        reference_time: datetime | None = None,
    ) -> bool:
        current_time = reference_time or now_utc()
        session_start = self._to_utc_aware(exam.session.start_at)
        session_end = self._to_utc_aware(exam.session.end_at)
        return session_start <= current_time < session_end

    def _build_audit_event_response(self, event: ExamAuditEvent) -> AuditEventDetailedResponse:
        return AuditEventDetailedResponse(
            id=event.id,
            exam_id=event.exam_id,
            from_status=event.from_status,
            to_status=event.to_status,
            note=event.note,
            performed_at=event.performed_at,
            meta=event.meta,
            performed_by=AuditPerformedByResponse(
                id=event.performed_by.id,
                username=event.performed_by.username,
                full_name=event.performed_by.full_name,
            ),
        )
