from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, InactiveUserError, ResourceNotFoundError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.technician import Technician
from app.services.auth_service import AuthService


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_technician(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Technician:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticazione richiesta.",
        )

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")

        if subject is None:
            raise AuthenticationError("Token privo di subject.")

        try:
            technician_id = int(subject)
        except (TypeError, ValueError) as exc:
            raise AuthenticationError("Subject del token non valido.") from exc

        auth_service = AuthService()
        return auth_service.get_current_technician(db, technician_id=technician_id)

    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
