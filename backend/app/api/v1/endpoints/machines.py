from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.db.session import get_db
from app.dependencies.auth import get_current_technician
from app.models.enums import MachineCode
from app.models.technician import Technician
from app.schemas.common import ErrorResponse
from app.schemas.machine import MachineResponse, MachineWorklistResponse
from app.services.worklist_service import WorklistService

router = APIRouter(prefix="/machines", tags=["machines"])


@router.get(
    "",
    response_model=list[MachineResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Autenticazione richiesta o token non valido.",
        },
    },
)
def list_machines(
    _current_technician: Technician = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> list[MachineResponse]:
    service = WorklistService()
    return service.list_machines(db)


@router.get(
    "/{machine_code}/worklist",
    response_model=MachineWorklistResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Autenticazione richiesta o token non valido.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Macchina non trovata.",
        },
    },
)
def get_machine_worklist(
    machine_code: MachineCode,
    _current_technician: Technician = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> MachineWorklistResponse:
    service = WorklistService()

    try:
        return service.get_machine_worklist(db, machine_code=machine_code)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
