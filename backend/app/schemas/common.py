from pydantic import BaseModel, ConfigDict, Field


class ORMBaseSchema(BaseModel):

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):

    message: str = Field(..., description="Messaggio descrittivo dell'esito.")


class ErrorResponse(BaseModel):

    detail: str = Field(..., description="Descrizione sintetica dell'errore.")
