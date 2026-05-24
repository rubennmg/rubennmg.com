import uuid

from pydantic import BaseModel


class RankingGame(BaseModel):
    slug: str
    display_name: str


class RankingSummary(BaseModel):
    total_players: int
    total_matches: int


class RankingRow(BaseModel):
    position: int
    player_id: uuid.UUID
    player_name: str
    matches_played: int
    wins: int
    total_points: int
    average_points: float
    win_rate: float


class RankingResponse(BaseModel):
    game: RankingGame
    summary: RankingSummary
    ranking: list[RankingRow]
