import uuid

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    role: str


class LoginResponse(BaseModel):
    user: AuthUser


class CsrfResponse(BaseModel):
    csrf_token: str
