import uuid

from pydantic import BaseModel, ConfigDict


class GameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    display_name: str
    description: str | None
    is_active: bool
    ranking_strategy: str
    min_players: int
