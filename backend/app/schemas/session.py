from datetime import datetime

from pydantic import Field

from app.models.enums import SessionStatus
from app.schemas.common import ORMBaseSchema


class SessionTechnicianInfo(ORMBaseSchema):

    id: int = Field(..., description="ID del tecnico assegnato alla sessione.")
    full_name: str = Field(..., description="Nome completo del tecnico assegnato.")


class SessionMachineInfo(ORMBaseSchema):

    id: int = Field(..., description="ID della macchina.")
    code: str = Field(..., description="Codice macchina: RM, TC o RX.")
    display_name: str = Field(..., description="Nome descrittivo della macchina.")


class SessionSummaryResponse(ORMBaseSchema):

    id: int = Field(..., description="Identificativo univoco della sessione.")
    start_at: datetime = Field(..., description="Inizio sessione in UTC.")
    end_at: datetime = Field(..., description="Fine sessione in UTC.")
    status: SessionStatus = Field(..., description="Stato corrente della sessione.")

    machine: SessionMachineInfo = Field(
        ...,
        description="Macchina associata alla sessione.",
    )
    technician: SessionTechnicianInfo = Field(
        ...,
        description="Tecnico assegnato alla sessione.",
    )


class SessionListItemResponse(ORMBaseSchema):

    id: int = Field(..., description="Identificativo univoco della sessione.")
    start_at: datetime = Field(..., description="Inizio sessione in UTC.")
    end_at: datetime = Field(..., description="Fine sessione in UTC.")
    status: SessionStatus = Field(..., description="Stato della sessione.")
    is_active_now: bool = Field(
        ...,
        description="Indica se la sessione è quella da evidenziare come attiva.",
    )
    technician_id: int = Field(..., description="ID del tecnico assegnato.")
    technician_name: str = Field(..., description="Nome del tecnico assegnato.")
