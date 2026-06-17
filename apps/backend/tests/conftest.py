from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.rate_limit import login_rate_limiter
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


@pytest.fixture()
def authenticated_client(client: TestClient) -> TestClient:
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "secret"}
    )
    assert response.status_code == 200
    assert settings.auth_cookie_name in client.cookies
    return client


@pytest.fixture()
def csrf_token(authenticated_client: TestClient) -> str:
    response = authenticated_client.get("/api/auth/csrf")
    assert response.status_code == 200
    return str(response.json()["csrf_token"])
