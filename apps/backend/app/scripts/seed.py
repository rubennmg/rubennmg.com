import argparse

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.db.base  # noqa: F401
from app.core.config import settings
from app.core.passwords import hash_password
from app.db.session import SessionLocal
from app.models.game import Game
from app.models.user import User

BASE_GAMES = [
    {
        "slug": "catan",
        "display_name": "Catán",
        "description": "Ranking de partidas de Catán.",
        "ranking_strategy": "catan_default",
        "min_players": 3,
    },
    {
        "slug": "flipseven",
        "display_name": "Flip Seven",
        "description": "Ranking de partidas de Flip Seven.",
        "ranking_strategy": "flipseven_default",
        "min_players": 2,
    },
]


def seed_games(db: Session, missing_only: bool = False) -> None:
    for game_data in BASE_GAMES:
        game = db.scalar(select(Game).where(Game.slug == game_data["slug"]))
        if game is None:
            db.add(Game(**game_data))
            continue

        if missing_only:
            continue

        game.display_name = game_data["display_name"]
        game.description = game_data["description"]
        game.ranking_strategy = game_data["ranking_strategy"]
        game.min_players = game_data["min_players"]
        game.is_active = True


def seed_admin(db: Session, username: str, password: str, missing_only: bool = False) -> None:
    user = db.scalar(select(User).where(User.username == username))
    if user is not None:
        if missing_only:
            return
        user.role = "admin"
        user.is_active = True
        return

    db.add(
        User(
            username=username,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
    )


def seed_database(
    db: Session, admin_username: str | None = None, admin_password: str | None = None,
    *, missing_only: bool = False,
) -> None:
    seed_games(db, missing_only=missing_only)
    seed_admin(
        db,
        username=admin_username or settings.admin_username,
        password=admin_password or settings.admin_password,
        missing_only=missing_only,
    )
    db.commit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--missing-only", action="store_true", help="Create missing games/admin without changing existing records")
    args = parser.parse_args()
    with SessionLocal() as db:
        seed_database(db, missing_only=args.missing_only)


if __name__ == "__main__":
    main()
