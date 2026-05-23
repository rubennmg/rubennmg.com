# rubennmg.com

Personal website and future full-stack application for experiments, tools and board game rankings.

## Repository Structure

This repository is moving towards a monorepo structure:

```txt
apps/
  frontend/   Astro static frontend
```

The current production site is still the static Astro frontend deployed at `rubennmg.com`.

## Branches

- `main`: current production branch for `rubennmg.com`.
- `develop`: staging branch for the future VPS environment at `rubennmg.cloud`.
- `feature/*`: day-to-day work branches targeting `develop`.

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

## Roadmap

The next infrastructure iterations will add a minimal FastAPI backend, PostgreSQL, Docker Compose staging, Caddy, deployment workflows and documentation. Business features such as admin login and rankings are intentionally deferred until the base infrastructure is ready.
