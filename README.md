# rubennmg.com

Personal website and future full-stack application for experiments, tools and board game rankings.

## Architecture

The project is now organized as a monorepo prepared for a gradual full-stack migration.

Current environments:

- `rubennmg.com`: production static Astro frontend on Hostinger Premium Web Hosting.
- `rubennmg.cloud`: staging frontend on the VPS.
- `api.rubennmg.cloud`: staging FastAPI backend on the VPS.

Business features such as admin login, CRUD and rankings are intentionally deferred until the infrastructure base is stable.

## Repository Structure

```txt
apps/
  frontend/   Astro static frontend served by nginx in Docker
  backend/    FastAPI backend prepared for PostgreSQL
infra/
  staging/    Docker Compose stack and Caddy config
docs/         Architecture, deployment and operations docs
.github/      CI, CD and Dependabot configuration
```

## Branches

- `main`: current production branch for `rubennmg.com`.
- `develop`: staging branch for `rubennmg.cloud`.
- `feature/*`: day-to-day work branches targeting `develop`.
- `hotfix/*`: urgent production fixes from `main`.

See `docs/git-workflow.md` for the full workflow.

## Frontend

Run the Astro frontend locally from `apps/frontend`:

```bash
cd apps/frontend
npm ci
npm run dev
```

Build it with:

```bash
cd apps/frontend
npm run build
```

Build the frontend Docker image:

```bash
docker build -t rubennmg-frontend ./apps/frontend
```

## Backend

Run the FastAPI backend locally from `apps/backend`:

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

Health endpoints:

- `GET /health`
- `GET /api/health`
- `GET /api/health/db`

Build the backend Docker image:

```bash
docker build -t rubennmg-backend ./apps/backend
```

## Staging Stack

Create a local staging env file from the template:

```bash
cd infra/staging
cp ../../.env.example .env.staging
```

Start the stack:

```bash
docker compose --env-file .env.staging -f compose.yml up -d --build
```

Stop it:

```bash
docker compose --env-file .env.staging -f compose.yml down
```

PostgreSQL is private to Docker and is not exposed on the host.

## CI/CD

- CI runs on pushes and PRs to `develop` and `main`.
- Staging deploy runs on pushes to `develop`.
- Production Premium deploy runs on pushes to `main`.
- Merged same-repo `feature/*` branches targeting `develop` are deleted automatically.
- Dependabot opens dependency PRs against `develop`.

## Documentation

- `docs/architecture.md`
- `docs/git-workflow.md`
- `docs/local-development.md`
- `docs/deployment-staging.md`
- `docs/deployment-production-premium.md`
- `docs/environment-variables.md`
- `docs/operations.md`
