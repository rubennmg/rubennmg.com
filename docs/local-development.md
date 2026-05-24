# Local Development

This guide covers two local workflows:

- Manual development: PostgreSQL in Docker, backend and frontend running on the host.
- Docker Compose development: PostgreSQL, backend and frontend running in containers with hot reload.

Local URLs:

- Frontend: `http://localhost:4321`
- Backend API: `http://localhost:8000`
- Backend docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

Default local admin credentials:

- Username: `admin`
- Password: `change-me`

## Manual Development

Start only PostgreSQL with the local Compose file:

```bash
docker compose -f infra/local/compose.yml up -d db
```

Run the backend from the host:

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -e .

export APP_ENV=development
export DATABASE_URL=postgresql+psycopg://rubennmg:change-me@localhost:5432/rubennmg_local
export CORS_ALLOWED_ORIGINS=http://localhost:4321,http://127.0.0.1:4321
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=change-me
export ENABLE_DEMO_DATA=false
export AUTH_SECRET_KEY=local-development-secret
export AUTH_COOKIE_NAME=rubennmg_session
export AUTH_SESSION_DAYS=7

alembic upgrade head
python -m app.scripts.seed
uvicorn app.main:app --reload
```

Run the frontend from another terminal:

```bash
cd apps/frontend
npm ci
PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Useful checks:

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/health/db
curl http://localhost:8000/api/games/catan/rankings
```

Open the public pages:

- `http://localhost:4321/games/catan`
- `http://localhost:4321/games/catan/rankings`
- `http://localhost:4321/games/flipseven`
- `http://localhost:4321/games/flipseven/rankings`

Stop the local database:

```bash
docker compose -f infra/local/compose.yml down
```

Remove local database data if you need a clean database:

```bash
docker compose -f infra/local/compose.yml down -v
```

## Docker Compose Development

Start the full local development stack:

```bash
docker compose -f infra/local/compose.yml up --build
```

The backend container installs the package, runs migrations, seeds base games/admin user, and starts `uvicorn` with reload. The frontend container runs Astro dev server with `PUBLIC_API_URL=http://localhost:8000`.

Run it in the background if preferred:

```bash
docker compose -f infra/local/compose.yml up -d --build
```

View logs:

```bash
docker compose -f infra/local/compose.yml logs -f backend frontend
```

Stop the stack:

```bash
docker compose -f infra/local/compose.yml down
```

Reset the local database and frontend container dependencies volume:

```bash
docker compose -f infra/local/compose.yml down -v
```

## Notes

- The local Compose stack is for development only and intentionally hardcodes safe local defaults.
- The local database name is `rubennmg_local`, separate from staging's `rubennmg_staging`.
- PostgreSQL is exposed on `localhost:5432` for manual development and database inspection.
- Do not use `infra/local/compose.yml` for staging or production deployments.
