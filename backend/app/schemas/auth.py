from pydantic import Field

from app.schemas.common import ORMBaseSchema


class LoginRequest(ORMBaseSchema):

    username: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Username del tecnico radiologo.",
        examples=["Amaggio"],
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Password in chiaro inserita in fase di login.",
        examples=["Alessiom92!"],
    )


class TokenResponse(ORMBaseSchema):

    access_token: str = Field(
        ...,
        description="JWT da usare nell'header Authorization come Bearer token.",
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo di token restituito dal backend.",
        examples=["bearer"],
    )


class AuthenticatedTechnicianResponse(ORMBaseSchema):

    id: int = Field(..., description="Identificativo univoco del tecnico.")
    username: str = Field(..., description="Username del tecnico.")
    full_name: str = Field(..., description="Nome completo del tecnico.")
    is_active: bool = Field(..., description="Flag di abilitazione dell'account.")


class LoginResponse(ORMBaseSchema):

    access_token: str = Field(
        ...,
        description="JWT da usare per autenticare le chiamate successive.",
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo di token restituito dal backend.",
    )
    technician: AuthenticatedTechnicianResponse = Field(
        ...,
        description="Profilo essenziale del tecnico autenticato.",
    )
