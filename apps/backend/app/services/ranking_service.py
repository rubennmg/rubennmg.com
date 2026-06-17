from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.game import Game
from app.models.match import Match
from app.models.match_result import MatchResult
from app.models.player import Player
from app.ranking.strategies import get_ranking_sort_key
from app.schemas.ranking import RankingGame, RankingResponse, RankingRow, RankingSummary


def build_ranking(db: Session, game: Game) -> RankingResponse:
    total_matches = (
        db.scalar(
            select(func.count(Match.id)).where(
                Match.game_id == game.id, Match.is_deleted.is_(False)
            )
        )
        or 0
    )

    rows = db.execute(
        select(
            Player.id,
            Player.display_name,
            func.count(MatchResult.id).label("matches_played"),
            func.sum(MatchResult.score).label("total_points"),
            func.sum(case((MatchResult.is_winner.is_(True), 1), else_=0)).label("wins"),
        )
        .join(MatchResult, MatchResult.player_id == Player.id)
        .join(Match, Match.id == MatchResult.match_id)
        .where(Match.game_id == game.id, Match.is_deleted.is_(False))
        .group_by(Player.id, Player.display_name)
    ).all()

    ranking_rows = []
    for row in rows:
        matches_played = int(row.matches_played or 0)
        wins = int(row.wins or 0)
        total_points = int(row.total_points or 0)
        average_points = (
            round(total_points / matches_played, 2) if matches_played else 0.0
        )
        win_rate = round((wins / matches_played) * 100, 2) if matches_played else 0.0
        ranking_rows.append(
            RankingRow(
                position=0,
                player_id=row.id,
                player_name=row.display_name,
                matches_played=matches_played,
                wins=wins,
                total_points=total_points,
                average_points=average_points,
                win_rate=win_rate,
            )
        )

    sort_key = get_ranking_sort_key(game.ranking_strategy)
    sorted_rows = sorted(ranking_rows, key=sort_key)
    for index, row in enumerate(sorted_rows, start=1):
        row.position = index

    return RankingResponse(
        game=RankingGame(slug=game.slug, display_name=game.display_name),
        summary=RankingSummary(
            total_players=len(sorted_rows), total_matches=total_matches
        ),
        ranking=sorted_rows,
    )
