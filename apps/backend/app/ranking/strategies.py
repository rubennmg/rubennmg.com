from collections.abc import Callable

from app.schemas.ranking import RankingRow


def catan_sort_key(row: RankingRow) -> tuple[float | int | str, ...]:
    return (
        -row.wins,
        -row.average_points,
        -row.total_points,
        -row.matches_played,
        row.player_name.lower(),
    )


def flipseven_sort_key(row: RankingRow) -> tuple[float | int | str, ...]:
    return (
        -row.wins,
        -row.total_points,
        -row.average_points,
        -row.matches_played,
        row.player_name.lower(),
    )


RANKING_STRATEGIES: dict[str, Callable[[RankingRow], tuple[float | int | str, ...]]] = {
    "catan_default": catan_sort_key,
    "flipseven_default": flipseven_sort_key,
}


def get_ranking_sort_key(
    strategy: str,
) -> Callable[[RankingRow], tuple[float | int | str, ...]]:
    return RANKING_STRATEGIES.get(strategy, catan_sort_key)
