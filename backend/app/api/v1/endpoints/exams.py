from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthorizationError,
    InvalidStateTransitionError,
    MissingCancellationNoteError,
    ResourceNotFoundError,
)
from app.db.session import get_db
from app.dependencies.auth import get_current_technician
from app.models.technician import Technician
from app.schemas.audit import AuditEventDetailedResponse
from app.schemas.common import ErrorResponse
from app.schemas.exam import (
    ExamDetailResponse,
    ExamStateTransitionRequest,
    ExamStateTransitionResponse,
)
from app.services.exam_state_service import ExamStateService

router = APIRouter(prefix="/exams", tags=["exams"])


@router.get(
    "/{exam_id}",
    response_model=ExamDetailResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Autenticazione richiesta o token non valido.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Esame non trovato.",
        },
    },
)
def get_exam_detail(
    exam_id: int,
    current_technician: Technician = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> ExamDetailResponse:
    service = ExamStateService()

    try:
        return service.get_exam_detail(
            db,
            exam_id=exam_id,
            current_technician=current_technician,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{exam_id}/audit-events",
    response_model=list[AuditEventDetailedResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Autenticazione richiesta o token non valido.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Esame non trovato.",
        },
    },
)
def get_exam_audit_events(
    exam_id: int,
    _current_technician: Technician = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> list[AuditEventDetailedResponse]:
    service = ExamStateService()

    try:
        return service.list_audit_events(db, exam_id=exam_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{exam_id}/state-transitions",
    response_model=ExamStateTransitionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Nota obbligatoria mancante per CANCELLED.",
        },
        401: {
            "model": ErrorResponse,
            "description": "Autenticazione richiesta o token non valido.",
        },
        403: {
            "model": ErrorResponse,
            "description": "Tecnico non autorizzato su questa sessione.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Esame non trovato.",
        },
        409: {
            "model": ErrorResponse,
            "description": "Transizione di stato non valida.",
        },
    },
)
def change_exam_state(
    exam_id: int,
    payload: ExamStateTransitionRequest,
    current_technician: Technician = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> ExamStateTransitionResponse:
    service = ExamStateService()

    try:
        return service.request_state_change(
            db,
            exam_id=exam_id,
            target_status=payload.target_status,
            current_technician=current_technician,
            note=payload.note,
        )
    except MissingCancellationNoteError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except AuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidStateTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
