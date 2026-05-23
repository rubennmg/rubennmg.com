# Architecture

`rubennmg.com` is transitioning from a static Astro portfolio to a full-stack monorepo.

## Current Transition State

```txt
rubennmg.com
└── Hostinger Premium Web Hosting
    └── Production
        └── Static Astro frontend

rubennmg.cloud
└── VPS
    └── Staging
        ├── Caddy reverse proxy
        ├── Astro frontend container
        ├── FastAPI backend container
        └── PostgreSQL private Docker service
```

## Domains

- `rubennmg.com`: current production frontend on Premium Web Hosting.
- `www.rubennmg.com`: current production frontend on Premium Web Hosting.
- `rubennmg.cloud`: staging frontend on the VPS.
- `www.rubennmg.cloud`: staging frontend on the VPS.
- `api.rubennmg.cloud`: staging backend on the VPS.

## Repository Layout

```txt
apps/
  frontend/   Astro static frontend
  backend/    FastAPI backend
infra/
  staging/    Docker Compose and Caddy config
docs/         Project documentation
```

## Runtime Flow

```mermaid
flowchart TD
    Developer[Developer] --> GitHub[GitHub]
    GitHub --> Main[main]
    GitHub --> Develop[develop]

    Main --> PremiumDeploy[Production deploy]
    PremiumDeploy --> Premium[Premium Web Hosting]
    Premium --> Com[rubennmg.com]

    Develop --> StagingDeploy[Staging deploy]
    StagingDeploy --> VPS[VPS]
    VPS --> Caddy[Caddy]
    Caddy --> Frontend[Astro frontend]
    Caddy --> Backend[FastAPI backend]
    Backend --> Postgres[(PostgreSQL)]
```

## Included In v1

- Monorepo layout.
- Static Astro frontend under `apps/frontend`.
- Minimal FastAPI backend under `apps/backend`.
- Health endpoints.
- PostgreSQL prepared in Docker Compose for staging.
- Caddy reverse proxy for staging.
- GitHub Actions CI and CD workflows.
- Dependabot.
- Documentation.

## Not Included In v1

- Admin login.
- Cookies or auth sessions.
- Players CRUD.
- Matches CRUD.
- Real rankings.
- Functional `/admin` panel.
- Production backend on the VPS.
- CodeQL.
