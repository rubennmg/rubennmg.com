# rubennmg.com

Personal website and future full-stack application for experiments, tools and board game rankings.

## Architecture

The project is now organized as a monorepo prepared for a gradual full-stack migration.

Current environments:

- `rubennmg.com`: production frontend, FastAPI and PostgreSQL on the VPS.
- `rubennmg.cloud`: independent staging frontend, FastAPI and PostgreSQL on the same VPS.
- `api.rubennmg.cloud`: legacy staging API hostname; both frontends now use same-origin `/api`.

Admin login, player and match management, and public Catán and Flip Seven rankings are implemented. See `docs/board-games-rankings.md` for the current rules and verification workflow.

## Repository Structure

```txt
apps/
  frontend/   Astro static frontend served by nginx in Docker
  backend/    FastAPI backend prepared for PostgreSQL
infra/
  staging/    Staging Compose stack
  production/ Production Compose stack
  proxy/      Shared Caddy template
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

## VPS Stacks

Follow [the VPS deployment guide](docs/deployment-vps.md) to provision or migrate staging and production. It includes environment files, secrets, DNS, persistent volume preservation and the shared Caddy setup.

After provisioning, run the corresponding script from its dedicated checkout:

```bash
bash infra/staging/deploy.sh
# In the production checkout:
bash infra/production/deploy.sh
```

Only Caddy publishes public application ports. Each database has its own persistent external volume and private network.

## CI/CD

- CI runs on PRs to `develop`/`main`, on pushes to `main`, and before both deployments.
- Staging deploy runs on pushes to `develop`.
- Production VPS deploy runs on pushes to `main`.
- Merged same-repo `feature/*` branches targeting `develop` are deleted automatically.
- Dependabot opens dependency PRs against `develop`.

## Documentation

- `docs/architecture.md`
- `docs/board-games-rankings.md`
- `docs/git-workflow.md`
- `docs/local-development.md`
- `docs/deployment-staging.md`
- `docs/deployment-production.md`
- `docs/deployment-vps.md`
- `docs/environment-variables.md`
- `docs/operations.md`
