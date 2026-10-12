# Environment Variables

Real VPS settings are stored only in each checkout's ignored `.env` file, mode 600:

- `infra/staging/.env.staging`, from `.env.staging.example` in the same directory.
- `infra/production/.env.production`, from `.env.production.example` in the same directory.

`.env.example` at the repository root remains a staging-oriented reference. Use the environment-specific templates for deployments. Real env files are excluded from Docker build contexts.

| Variable | Meaning |
| --- | --- |
| `PUBLIC_API_URL` | Public build-time frontend API **origin**, empty for same-origin `/api/...`. Never put a secret here or use `/api` as the value. Local development may use `http://localhost:8000`. |
| `CORS_ALLOWED_ORIGINS` | Comma-separated HTTPS root/www origins for this environment only. |
| `ADMIN_USERNAME` | Initial seeded admin username. |
| `ADMIN_PASSWORD` | Independent secret per environment; only used when creating a missing admin. |
| `ENABLE_DEMO_DATA` | Keep `false` in normal deployment. |
| `AUTH_SECRET_KEY` | Independent random secret for signing sessions/CSRF tokens. |
| `AUTH_COOKIE_NAME` | `rubennmg_staging_session` or `rubennmg_production_session`. |
| `AUTH_SESSION_DAYS` | Session lifetime, default 7 days. |
| `POSTGRES_PASSWORD` | Independent URL-safe DB password; generate with `openssl rand -hex 32`. Preserve the existing staging password. |

VPS Compose fixes `APP_ENV` to `staging`/`production`, and constructs `DATABASE_URL` with the corresponding database (`rubennmg_staging`/`rubennmg_production`), user `rubennmg`, and private `db:5432` host. They need not be supplied manually. PostgreSQL initialization settings do not change credentials on an existing volume. The seed does not rotate an existing admin password.

GitHub Environments **staging** and **production** each require `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `VPS_KNOWN_HOSTS`. Environment scoping separates values; no `STAGING_`/`PRODUCTION_` prefix is needed. Application/DB secrets are not passed through GitHub Actions. FTP secrets are obsolete and can be removed.

See [deployment-vps.md](deployment-vps.md) for paths, host-key verification and first deployment.
