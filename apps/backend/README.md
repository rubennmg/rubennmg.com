# rubennmg API

Minimal FastAPI backend prepared for the future full-stack application.

## Local Development

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

Available endpoints:

- `GET /health`
- `GET /api/health`
- `GET /api/health/db`

The database endpoint expects `DATABASE_URL` to point to a reachable PostgreSQL instance.

## Database

Apply migrations:

```bash
alembic upgrade head
```

Seed base games and the initial admin user:

```bash
ADMIN_USERNAME=admin ADMIN_PASSWORD=change-me python -m app.scripts.seed
```

The seed is idempotent and can be run multiple times without duplicating games or users.

## Auth

Admin auth endpoints:

- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/auth/csrf`

Sessions are signed tokens stored in an HttpOnly cookie. Set `AUTH_SECRET_KEY` to a strong secret outside local development.
