import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_admin, require_csrf_token
from app.db.session import get_db
from app.models.game import Game
from app.models.match import Match
from app.models.match_result import MatchResult
from app.models.player import Player
from app.models.user import User
from app.schemas.match import MatchCreate, MatchRead, MatchResultInput, MatchUpdate

router = APIRouter(prefix="/api/admin/matches", tags=["admin matches"])


def _match_options():
    return (
        selectinload(Match.game),
        selectinload(Match.results).selectinload(MatchResult.player),
    )


def _get_active_game(db: Session, game_slug: str) -> Game:
    game = db.scalar(
        select(Game).where(Game.slug == game_slug, Game.is_active.is_(True))
    )
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )
    return game


def _validate_results(
    db: Session, game: Game, results: list[MatchResultInput]
) -> list[Player]:
    if len(results) < game.min_players:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{game.display_name} requires at least {game.min_players} players",
        )

    player_ids = [result.player_id for result in results]
    if len(player_ids) != len(set(player_ids)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Players cannot be repeated",
        )

    winners = [result for result in results if result.is_winner]
    if len(winners) != 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Exactly one winner is required",
        )

    if game.ranking_strategy == "catan_default" and any(
        result.position is None for result in results
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Catán matches require positions for every player",
        )

    players = list(
        db.scalars(
            select(Player).where(Player.id.in_(player_ids), Player.is_active.is_(True))
        )
    )
    if len(players) != len(player_ids):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="All players must exist and be active",
        )

    return players


def _apply_match_payload(
    db: Session, match: Match, payload: MatchCreate | MatchUpdate, user: User
) -> None:
    game = _get_active_game(db, payload.game_slug)
    _validate_results(db, game, payload.results)

    match.game = game
    match.played_at = payload.played_at
    match.notes = payload.notes
    if match.created_by_user_id is None:
        match.created_by_user_id = user.id
    if match.id is not None:
        match.results.clear()
        db.flush()
    match.results = [
        MatchResult(
            player_id=result.player_id,
            score=result.score,
            position=result.position,
            is_winner=result.is_winner,
        )
        for result in payload.results
    ]


def _get_match_or_404(db: Session, match_id: uuid.UUID) -> Match:
    match = db.scalar(
        select(Match)
        .options(*_match_options())
        .where(Match.id == match_id, Match.is_deleted.is_(False))
    )
    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )
    return match


@router.get("", response_model=list[MatchRead])
def list_matches(
    game: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[Match]:
    query = (
        select(Match)
        .options(*_match_options())
        .where(Match.is_deleted.is_(False))
        .order_by(Match.played_at.desc())
    )
    if game:
        query = query.join(Match.game).where(Game.slug == game)
    return list(db.scalars(query))


@router.post("", response_model=MatchRead, status_code=status.HTTP_201_CREATED)
def create_match(
    payload: MatchCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    _csrf: None = Depends(require_csrf_token),
) -> Match:
    match = Match()
    _apply_match_payload(db, match, payload, admin)
    db.add(match)
    db.commit()
    return _get_match_or_404(db, match.id)


@router.get("/{match_id}", response_model=MatchRead)
def get_match(
    match_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Match:
    return _get_match_or_404(db, match_id)


@router.put("/{match_id}", response_model=MatchRead)
def update_match(
    match_id: uuid.UUID,
    payload: MatchUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    _csrf: None = Depends(require_csrf_token),
) -> Match:
    match = _get_match_or_404(db, match_id)
    _apply_match_payload(db, match, payload, admin)
    db.commit()
    return _get_match_or_404(db, match.id)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(
    match_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    _csrf: None = Depends(require_csrf_token),
) -> None:
    match = _get_match_or_404(db, match_id)
    match.is_deleted = True
    db.commit()
