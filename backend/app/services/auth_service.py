from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, InactiveUserError, ResourceNotFoundError
from app.core.security import create_access_token, verify_password
from app.models.technician import Technician
from app.repositories.technician_repository import TechnicianRepository


class AuthService:

    def __init__(self) -> None:
        self.technician_repository = TechnicianRepository()

    def authenticate(self, db: Session, *, username: str, password: str) -> tuple[str, Technician]:
        technician = self.technician_repository.get_by_username(db, username)


        if technician is None:
            raise AuthenticationError("Credenziali non valide.")

        password_is_valid = verify_password(password, technician.password_hash)
        if not password_is_valid:
            raise AuthenticationError("Credenziali non valide.")

        if not technician.is_enabled():
            raise InactiveUserError("Account non abilitato all'accesso.")

        access_token = create_access_token(subject=str(technician.id))
        return access_token, technician

    def get_current_technician(self, db: Session, *, technician_id: int) -> Technician:
        technician = self.technician_repository.get_by_id(db, technician_id)
        if technician is None:
            raise ResourceNotFoundError("Tecnico autenticato non trovato.")

        if not technician.is_enabled():
            raise InactiveUserError("Account non abilitato all'accesso.")

        return technician
