from datetime import datetime

from pydantic import Field

from app.models.enums import ExamStatus, MachineCode, SessionStatus
from app.schemas.common import ORMBaseSchema


class MachineResponse(ORMBaseSchema):

    id: int = Field(..., description="ID della macchina.")
    code: MachineCode = Field(..., description="Codice macchina.")
    display_name: str = Field(..., description="Nome visualizzato della macchina.")
    is_active: bool = Field(..., description="Flag di attivazione macchina.")


class WorklistPatientResponse(ORMBaseSchema):

    id: int = Field(..., description="ID del paziente.")
    patient_code: str = Field(..., description="Codice identificativo paziente.")
    first_name: str = Field(..., description="Nome del paziente.")
    last_name: str = Field(..., description="Cognome del paziente.")


class WorklistExamResponse(ORMBaseSchema):

    id: int = Field(..., description="ID dell'esame.")
    exam_code: str = Field(..., description="Codice univoco dell'esame.")
    scheduled_time: datetime = Field(
        ...,
        description="Orario pianificato dell'esame in UTC.",
    )
    status: ExamStatus = Field(..., description="Stato corrente dell'esame.")
    session_id: int = Field(..., description="ID della sessione di appartenenza.")
    patient: WorklistPatientResponse = Field(
        ...,
        description="Dati essenziali del paziente.",
    )


class WorklistSessionResponse(ORMBaseSchema):

    id: int = Field(..., description="ID della sessione.")
    start_at: datetime = Field(..., description="Inizio sessione in UTC.")
    end_at: datetime = Field(..., description="Fine sessione in UTC.")
    status: SessionStatus = Field(..., description="Stato della sessione.")
    technician_id: int = Field(..., description="ID del tecnico assegnato.")
    technician_name: str = Field(..., description="Nome del tecnico assegnato.")
    is_active_now: bool = Field(
        ...,
        description="Flag calcolato per evidenza della sessione attiva.",
    )
    exams: list[WorklistExamResponse] = Field(
        default_factory=list,
        description="Elenco esami della sessione.",
    )


class MachineWorklistResponse(ORMBaseSchema):

    machine: MachineResponse = Field(
        ...,
        description="Macchina per cui si richiede la worklist.",
    )
    generated_at: datetime = Field(
        ...,
        description="Timestamp UTC di generazione della risposta.",
    )
    active_session_id: int | None = Field(
        None,
        description="ID della sessione da evidenziare come attiva, se presente.",
    )
    sessions: list[WorklistSessionResponse] = Field(
        default_factory=list,
        description="Sessioni della macchina con relativi esami.",
    )
