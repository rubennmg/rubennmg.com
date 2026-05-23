import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_admin, require_csrf_token
from app.db.session import get_db
from app.models.player import Player
from app.models.user import User
from app.schemas.player import (
    PlayerCreate,
    PlayerRead,
    PlayerStatusUpdate,
    PlayerUpdate,
)

router = APIRouter(prefix="/api/admin/players", tags=["admin players"])


@router.get("", response_model=list[PlayerRead])
def list_players(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[Player]:
    return list(db.scalars(select(Player).order_by(Player.display_name)))


@router.post("", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
def create_player(
    payload: PlayerCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    _csrf: None = Depends(require_csrf_token),
) -> Player:
    player = Player(
        display_name=payload.display_name,
        nickname=payload.nickname,
        avatar_url=payload.avatar_url,
        is_active=True,
    )
    db.add(player)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Player display_name already exists",
        ) from exc

    db.refresh(player)
    return player


@router.get("/{player_id}", response_model=PlayerRead)
def get_player(
    player_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Player:
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )
    return player


@router.put("/{player_id}", response_model=PlayerRead)
def update_player(
    player_id: uuid.UUID,
    payload: PlayerUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    _csrf: None = Depends(require_csrf_token),
) -> Player:
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )

    player.display_name = payload.display_name
    player.nickname = payload.nickname
    player.avatar_url = payload.avatar_url

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Player display_name already exists",
        ) from exc

    db.refresh(player)
    return player


@router.patch("/{player_id}/status", response_model=PlayerRead)
def update_player_status(
    player_id: uuid.UUID,
    payload: PlayerStatusUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    _csrf: None = Depends(require_csrf_token),
) -> Player:
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )

    player.is_active = payload.is_active
    db.commit()
    db.refresh(player)
    return player
