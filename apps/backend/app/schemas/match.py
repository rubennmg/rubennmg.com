import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MatchResultInput(BaseModel):
    player_id: uuid.UUID
    score: int = Field(ge=0)
    position: int | None = Field(default=None, ge=1)
    is_winner: bool = False


class MatchCreate(BaseModel):
    game_slug: str
    played_at: datetime
    notes: str | None = None
    results: list[MatchResultInput]


class MatchUpdate(BaseModel):
    game_slug: str
    played_at: datetime
    notes: str | None = None
    results: list[MatchResultInput]


class MatchGameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    display_name: str


class MatchPlayerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str


class MatchResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    player: MatchPlayerRead
    score: int
    position: int | None
    is_winner: bool


class MatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    game: MatchGameRead
    played_at: datetime
    notes: str | None
    is_deleted: bool
    results: list[MatchResultRead]
    created_at: datetime
    updated_at: datetime
