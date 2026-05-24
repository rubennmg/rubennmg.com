from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.game import Game
from app.schemas.game import GameRead
from app.schemas.ranking import RankingResponse
from app.services.ranking_service import build_ranking

router = APIRouter(prefix="/api/games", tags=["public games"])


def _get_active_game(db: Session, game_slug: str) -> Game:
    game = db.scalar(
        select(Game).where(Game.slug == game_slug, Game.is_active.is_(True))
    )
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )
    return game


@router.get("", response_model=list[GameRead])
def list_games(db: Session = Depends(get_db)) -> list[Game]:
    return list(
        db.scalars(
            select(Game).where(Game.is_active.is_(True)).order_by(Game.display_name)
        )
    )


@router.get("/{game_slug}", response_model=GameRead)
def get_game(game_slug: str, db: Session = Depends(get_db)) -> Game:
    return _get_active_game(db, game_slug)


@router.get("/{game_slug}/rankings", response_model=RankingResponse)
def get_game_ranking(game_slug: str, db: Session = Depends(get_db)) -> RankingResponse:
    game = _get_active_game(db, game_slug)
    return build_ranking(db, game)
