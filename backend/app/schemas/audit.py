from datetime import datetime
from typing import Any

from pydantic import Field

from app.models.enums import ExamStatus
from app.schemas.common import ORMBaseSchema


class AuditPerformedByResponse(ORMBaseSchema):

    id: int = Field(..., description="ID del tecnico.")
    username: str = Field(..., description="Username del tecnico.")
    full_name: str = Field(..., description="Nome completo del tecnico.")


class AuditEventResponse(ORMBaseSchema):

    id: int = Field(..., description="ID univoco dell'evento audit.")
    exam_id: int = Field(..., description="ID dell'esame coinvolto.")
    performed_by_technician_id: int = Field(
        ...,
        description="ID del tecnico che ha eseguito la transizione.",
    )
    from_status: ExamStatus = Field(..., description="Stato precedente.")
    to_status: ExamStatus = Field(..., description="Nuovo stato.")
    note: str | None = Field(
        None,
        description="Nota associata alla transizione, se presente.",
    )
    performed_at: datetime = Field(
        ...,
        description="Timestamp UTC dell'evento di audit.",
    )
    meta: dict[str, Any] | None = Field(
        None,
        description="Eventuali metadati applicativi serializzabili.",
    )


class AuditEventDetailedResponse(ORMBaseSchema):

    id: int = Field(..., description="ID univoco dell'evento audit.")
    exam_id: int = Field(..., description="ID dell'esame coinvolto.")
    from_status: ExamStatus = Field(..., description="Stato precedente.")
    to_status: ExamStatus = Field(..., description="Nuovo stato.")
    note: str | None = Field(
        None,
        description="Nota associata alla transizione, se presente.",
    )
    performed_at: datetime = Field(
        ...,
        description="Timestamp UTC dell'evento di audit.",
    )
    meta: dict[str, Any] | None = Field(
        None,
        description="Metadati applicativi opzionali.",
    )
    performed_by: AuditPerformedByResponse = Field(
        ...,
        description="Tecnico che ha eseguito la transizione.",
    )
