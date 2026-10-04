from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.models.game import Game
from app.models.match import Match
from app.models.match_result import CatanResult, MatchResult
from app.models.player import Player
from app.ranking.strategies import get_ranking_sort_key
from app.schemas.ranking import CatanPlayerStatistics, RankingGame, RankingResponse, RankingRow, RankingSummary


COUNT_FIELDS = ("cities", "settlements", "roads", "victory_point_cards")
AWARD_FIELDS = ("longest_road", "largest_army")


def catan_statistics(db: Session, game: Game) -> dict:
    columns = [
        MatchResult.player_id,
        func.count(CatanResult.result_id).label("matches_with_details"),
    ]
    for field in COUNT_FIELDS + AWARD_FIELDS:
        column = getattr(CatanResult, field)
        columns.append(func.count(column).label(f"{field}_count"))
        if field in COUNT_FIELDS:
            columns.extend([
                func.sum(column).label(f"{field}_total"),
                func.avg(column).label(f"{field}_average"),
                func.max(column).label(f"{field}_best"),
            ])
        else:
            columns.append(func.sum(case((column.is_(True), 1), else_=0)).label(f"{field}_total"))
    rows = db.execute(
        select(*columns)
        .select_from(MatchResult)
        .join(Match, Match.id == MatchResult.match_id)
        .join(CatanResult, CatanResult.result_id == MatchResult.id)
        .where(Match.game_id == game.id, Match.is_deleted.is_(False))
        .group_by(MatchResult.player_id)
    ).mappings()
    return {row["player_id"]: row for row in rows}


def format_catan_statistics(stats) -> CatanPlayerStatistics:
    stats = stats or {}
    details = {"matches_with_details": stats.get("matches_with_details", 0)}
    for field in COUNT_FIELDS:
        average = stats.get(f"{field}_average")
        details[field] = {
            "recorded_matches": stats.get(f"{field}_count", 0),
            "total": stats.get(f"{field}_total") or 0,
            "average": round(float(average), 2) if average is not None else None,
            "best": stats.get(f"{field}_best"),
        }
    for field in AWARD_FIELDS:
        count = stats.get(f"{field}_count", 0)
        total = stats.get(f"{field}_total") or 0
        details[field] = {
            "recorded_matches": count,
            "times_held": total,
            "rate": round(total / count * 100, 2) if count else None,
        }
    return CatanPlayerStatistics(**details)


def build_ranking(db: Session, game: Game) -> RankingResponse:
    total_matches = (
        db.scalar(
            select(func.count(Match.id)).where(
                Match.game_id == game.id, Match.is_deleted.is_(False)
            )
        )
        or 0
    )

    game_stats = (
        select(
            MatchResult.player_id,
            func.count(MatchResult.id).label("matches_played"),
            func.sum(MatchResult.score).label("total_points"),
            func.sum(case((MatchResult.is_winner.is_(True), 1), else_=0)).label("wins"),
        )
        .join(Match, Match.id == MatchResult.match_id)
        .where(Match.game_id == game.id, Match.is_deleted.is_(False))
        .group_by(MatchResult.player_id)
        .subquery()
    )
    rows = db.execute(
        select(
            Player.id,
            Player.display_name,
            game_stats.c.matches_played,
            game_stats.c.total_points,
            game_stats.c.wins,
        )
        .outerjoin(game_stats, game_stats.c.player_id == Player.id)
        .where(or_(Player.is_active.is_(True), game_stats.c.matches_played > 0))
    ).all()

    catan_stats = catan_statistics(db, game) if game.slug == "catan" else {}
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
                catan=format_catan_statistics(catan_stats.get(row.id)) if game.slug == "catan" else None,
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
