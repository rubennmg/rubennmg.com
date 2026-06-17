import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlayerCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=150)
    nickname: str | None = Field(default=None, max_length=150)
    avatar_url: str | None = None


class PlayerUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=150)
    nickname: str | None = Field(default=None, max_length=150)
    avatar_url: str | None = None


class PlayerStatusUpdate(BaseModel):
    is_active: bool


class PlayerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str
    nickname: str | None
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
