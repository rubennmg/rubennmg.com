from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

import app.db.base  # noqa: F401
from app.core.passwords import verify_password
from app.models.base import Base
from app.models.game import Game
from app.models.user import User
from app.scripts.seed import seed_database


def test_seed_database_creates_base_games_and_admin() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        seed_database(db, admin_username="admin", admin_password="secret")
        seed_database(db, admin_username="admin", admin_password="secret")

        games = db.scalars(select(Game).order_by(Game.slug)).all()
        admin = db.scalar(select(User).where(User.username == "admin"))

    assert [game.slug for game in games] == ["catan", "flipseven"]
    assert games[0].display_name == "Catán"
    assert games[0].ranking_strategy == "catan_default"
    assert games[0].min_players == 3
    assert games[1].ranking_strategy == "flipseven_default"
    assert games[1].min_players == 2

    assert admin is not None
    assert admin.role == "admin"
    assert admin.is_active is True
    assert admin.password_hash != "secret"
    assert verify_password("secret", admin.password_hash)
