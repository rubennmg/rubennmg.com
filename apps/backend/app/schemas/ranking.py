import uuid

from pydantic import BaseModel


class RankingGame(BaseModel):
    slug: str
    display_name: str


class RankingSummary(BaseModel):
    total_players: int
    total_matches: int


class CountStatistics(BaseModel):
    recorded_matches: int
    total: int
    average: float | None
    best: int | None


class AwardStatistics(BaseModel):
    recorded_matches: int
    times_held: int
    rate: float | None


class CatanPlayerStatistics(BaseModel):
    matches_with_details: int
    cities: CountStatistics
    settlements: CountStatistics
    roads: CountStatistics
    victory_point_cards: CountStatistics
    longest_road: AwardStatistics
    largest_army: AwardStatistics


class RankingRow(BaseModel):
    position: int
    player_id: uuid.UUID
    player_name: str
    matches_played: int
    wins: int
    total_points: int
    average_points: float
    win_rate: float
    catan: CatanPlayerStatistics | None = None


class RankingResponse(BaseModel):
    game: RankingGame
    summary: RankingSummary
    ranking: list[RankingRow]
