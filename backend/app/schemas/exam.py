from datetime import date, datetime

from pydantic import Field, field_validator

from app.models.enums import ExamStatus, MachineCode, SessionStatus
from app.schemas.audit import AuditEventDetailedResponse
from app.schemas.common import ORMBaseSchema


class ExamPatientResponse(ORMBaseSchema):

    id: int = Field(..., description="ID del paziente.")
    patient_code: str = Field(..., description="Codice identificativo del paziente.")
    first_name: str = Field(..., description="Nome del paziente.")
    last_name: str = Field(..., description="Cognome del paziente.")
    birth_date: date | None = Field(
        None,
        description="Data di nascita del paziente, se presente.",
    )
    sex: str | None = Field(
        None,
        description="Sesso del paziente, se disponibile.",
    )


class ExamMachineResponse(ORMBaseSchema):

    id: int = Field(..., description="ID della macchina.")
    code: MachineCode = Field(..., description="Codice macchina.")
    display_name: str = Field(..., description="Nome della macchina.")


class ExamSessionResponse(ORMBaseSchema):

    id: int = Field(..., description="ID della sessione.")
    start_at: datetime = Field(..., description="Inizio sessione in UTC.")
    end_at: datetime = Field(..., description="Fine sessione in UTC.")
    status: SessionStatus = Field(..., description="Stato della sessione.")
    technician_id: int = Field(..., description="ID del tecnico assegnato.")
    technician_name: str = Field(..., description="Nome del tecnico assegnato.")
    machine: ExamMachineResponse = Field(
        ...,
        description="Macchina associata alla sessione.",
    )


class ExamDetailResponse(ORMBaseSchema):

    id: int = Field(..., description="ID dell'esame.")
    exam_code: str = Field(..., description="Codice univoco dell'esame.")
    scheduled_time: datetime = Field(
        ...,
        description="Orario pianificato dell'esame in UTC.",
    )
    status: ExamStatus = Field(..., description="Stato corrente dell'esame.")
    status_updated_at: datetime = Field(
        ...,
        description="Timestamp UTC dell'ultimo aggiornamento di stato.",
    )
    allowed_transitions: list[ExamStatus] = Field(
        default_factory=list,
        description="Elenco degli stati target consentiti dalla FSM.",
    )
    patient: ExamPatientResponse = Field(
        ...,
        description="Dati del paziente associato all'esame.",
    )
    session: ExamSessionResponse = Field(
        ...,
        description="Sessione di appartenenza dell'esame.",
    )
    audit_events: list[AuditEventDetailedResponse] = Field(
        default_factory=list,
        description="Storico audit dell'esame.",
    )


class ExamStateTransitionRequest(ORMBaseSchema):

    target_status: ExamStatus = Field(
        ...,
        description="Nuovo stato richiesto per l'esame.",
        examples=["ARRIVED"],
    )
    note: str | None = Field(
        None,
        description="Nota opzionale, obbligatoria per CANCELLED.",
        examples=["Paziente non presentato."],
    )

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class ExamStateTransitionResponse(ORMBaseSchema):

    exam_id: int = Field(..., description="ID dell'esame aggiornato.")
    exam_code: str = Field(..., description="Codice dell'esame aggiornato.")
    previous_status: ExamStatus = Field(
        ...,
        description="Stato precedente dell'esame.",
    )
    current_status: ExamStatus = Field(
        ...,
        description="Nuovo stato corrente dell'esame.",
    )
    status_updated_at: datetime = Field(
        ...,
        description="Timestamp UTC dell'aggiornamento di stato.",
    )
    note: str | None = Field(
        None,
        description="Nota associata alla transizione, se presente.",
    )
    allowed_next_transitions: list[ExamStatus] = Field(
        default_factory=list,
        description="Transizioni consentite a partire dal nuovo stato.",
    )
    audit_event: AuditEventDetailedResponse = Field(
        ...,
        description="Evento audit generato dalla transizione.",
    )
