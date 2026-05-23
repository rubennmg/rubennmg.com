from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.rate_limit import login_rate_limiter
from app.core.security import verify_csrf_token
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.scripts.seed import seed_database


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    login_rate_limiter.reset()
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        seed_database(db, admin_username="admin", admin_password="secret")

    def override_get_db() -> Generator[Session, None, None]:
        with SessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        login_rate_limiter.reset()


def test_login_me_csrf_and_logout(client: TestClient) -> None:
    login_response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "secret"}
    )

    assert login_response.status_code == 200
    assert login_response.json()["user"]["username"] == "admin"
    assert settings.auth_cookie_name in client.cookies

    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["user"]["role"] == "admin"

    csrf_response = client.get("/api/auth/csrf")
    assert csrf_response.status_code == 200
    assert verify_csrf_token(
        client.cookies[settings.auth_cookie_name], csrf_response.json()["csrf_token"]
    )

    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 204
    assert settings.auth_cookie_name not in client.cookies

    assert client.get("/api/auth/me").status_code == 401


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "wrong"}
    )

    assert response.status_code == 401
    assert settings.auth_cookie_name not in client.cookies


def test_login_rate_limit_after_failed_attempts(client: TestClient) -> None:
    for _ in range(5):
        response = client.post(
            "/api/auth/login", json={"username": "admin", "password": "wrong"}
        )
        assert response.status_code == 401

    limited_response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "wrong"}
    )
    assert limited_response.status_code == 429
