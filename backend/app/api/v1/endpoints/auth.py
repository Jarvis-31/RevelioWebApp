from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, InactiveUserError
from app.db.session import get_db
from app.dependencies.auth import get_current_technician
from app.models.technician import Technician
from app.schemas.auth import (
    AuthenticatedTechnicianResponse,
    LoginRequest,
    LoginResponse,
)
from app.schemas.common import ErrorResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Credenziali non valide.",
        },
        403: {
            "model": ErrorResponse,
            "description": "Account non abilitato.",
        },
    },
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    auth_service = AuthService()

    try:
        access_token, technician = auth_service.authenticate(
            db,
            username=payload.username,
            password=payload.password,
        )
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    technician_response = AuthenticatedTechnicianResponse.model_validate(technician)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        technician=technician_response,
    )


@router.get(
    "/me",
    response_model=AuthenticatedTechnicianResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Token assente o non valido.",
        },
        403: {
            "model": ErrorResponse,
            "description": "Account non abilitato.",
        },
    },
)
def me(
    current_technician: Technician = Depends(get_current_technician),
) -> AuthenticatedTechnicianResponse:
    return AuthenticatedTechnicianResponse.model_validate(current_technician)
