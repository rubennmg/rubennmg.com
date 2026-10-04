import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CatanResultDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    cities: int | None = Field(default=None, ge=0, strict=True)
    settlements: int | None = Field(default=None, ge=0, strict=True)
    roads: int | None = Field(default=None, ge=0, strict=True)
    longest_road: bool | None = Field(default=None, strict=True)
    largest_army: bool | None = Field(default=None, strict=True)
    victory_point_cards: int | None = Field(default=None, ge=0, strict=True)


class MatchResultInput(BaseModel):
    player_id: uuid.UUID
    score: int = Field(ge=0)
    position: int | None = Field(default=None, ge=1)
    is_winner: bool = False
    catan: CatanResultDetails | None = None


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
    catan: CatanResultDetails | None = None


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
