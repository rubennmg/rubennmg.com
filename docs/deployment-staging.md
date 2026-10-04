# Staging Deployment

Staging runs on the VPS behind Caddy using Docker Compose.

## Domains

Create these DNS records for `rubennmg.cloud`:

```txt
A  @    VPS_IP
A  www  VPS_IP
A  api  VPS_IP
```

`rubennmg.com` remains on the current Premium Web Hosting during the transition.

## VPS Layout

Expected repository path:

```txt
/home/deploy/apps/rubennmg.com
```

Create a non-root deploy user and allow it to use Docker:

```bash
sudo adduser deploy
sudo usermod -aG docker deploy
```

Open only the required public ports:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

Clone the repository as `deploy`:

```bash
sudo su - deploy
mkdir -p /home/deploy/apps
cd /home/deploy/apps
git clone git@github.com:rubennmg/rubennmg.com.git
cd rubennmg.com
git checkout develop
```

The staging environment file must live at:

```txt
/home/deploy/apps/rubennmg.com/infra/staging/.env.staging
```

Create it from the root example:

```bash
cd /home/deploy/apps/rubennmg.com/infra/staging
cp ../../.env.example .env.staging
```

Set real values for `POSTGRES_PASSWORD`, `ADMIN_PASSWORD` and `AUTH_SECRET_KEY`; do not keep `change-me`. Use `APP_ENV=staging`, `PUBLIC_API_URL=https://api.rubennmg.cloud` and include `https://rubennmg.cloud,https://www.rubennmg.cloud` in `CORS_ALLOWED_ORIGINS`. The API URL is embedded when building the frontend. Because the database password is embedded in a connection URL, use a URL-safe password (for example, random hexadecimal).

## GitHub Actions Deploy

Staging deploy runs on pushes to `develop` through `.github/workflows/deploy-staging.yml`, after its reusable CI job succeeds (frontend build, backend tests, backend Docker build and deployment configuration checks). PRs still run CI independently. Do not configure branch protection to require the old standalone push-to-develop CI run; select the checks from the current workflows if necessary.

Create a GitHub environment named `staging` and add these secrets:

```txt
VPS_HOST
VPS_USER
VPS_SSH_KEY
```

Expected values:

```txt
VPS_HOST=your-vps-ip-or-hostname
VPS_USER=deploy
VPS_SSH_KEY=private SSH key allowed to connect as deploy
```

Generate a dedicated deploy key locally:

```bash
ssh-keygen -t ed25519 -C "github-actions-rubennmg-staging" -f ~/.ssh/rubennmg_staging_deploy
```

Install the public key on the VPS for the `deploy` user:

```bash
ssh-copy-id -i ~/.ssh/rubennmg_staging_deploy.pub deploy@VPS_HOST
```

Store the private key contents in `VPS_SSH_KEY`:

```bash
cat ~/.ssh/rubennmg_staging_deploy
```

The workflow connects by SSH, fetches the repository and deploys the exact commit that passed CI. If `origin/develop` has advanced, the obsolete deployment is skipped. The checkout at `/home/deploy/apps/rubennmg.com` is a dedicated deployment checkout: tracked files are reset to that commit.

It then invokes:

```bash
cd /home/deploy/apps/rubennmg.com
bash infra/staging/deploy.sh
```

The file `infra/staging/.env.staging` must already exist on the VPS before the first automatic deployment.

## Start Staging

From the repository root on the VPS, after checking out the intended version:

```bash
bash infra/staging/deploy.sh
```

The same script supports initial setup and later updates:

1. Validate the environment and build both images before touching running services.
2. Start PostgreSQL and wait for its health check.
3. Run `alembic upgrade head` using the new backend image.
4. Run `python -m app.scripts.seed --missing-only` to create missing games and the initial admin. Existing passwords, roles, activation flags and game settings are preserved.
5. Start the stack and wait for backend/frontend health checks.
6. Read the active games and their rankings through the API, then check the public frontend and database-health URL over HTTPS.

Requires Docker Compose with `up --wait` / `--wait-timeout`, Bash, and curl with `--retry-all-errors` on the VPS. DNS and ports 80/443 must be ready for the public checks.

Build, database readiness, migration or seed failures stop the script before replacing application containers. Later health-check failures mark deployment as failed; there is no automatic rollback. Inspect logs and fix or redeploy a compatible version. Never run `down -v` as part of deployment. Back up staging data before future destructive migrations; the Catán migration only adds a table. Running migrations against the live database assumes they are compatible with the previous application version.

## Check Services

From `infra/staging`:

```bash
docker compose --env-file .env.staging -f compose.yml ps
docker compose --env-file .env.staging -f compose.yml logs -f caddy
docker compose --env-file .env.staging -f compose.yml logs -f backend
```

Expected public checks once DNS points to the VPS:

```txt
https://rubennmg.cloud
https://rubennmg.cloud/games/
https://api.rubennmg.cloud/health
https://api.rubennmg.cloud/api/health/db
```

PostgreSQL is only attached to the internal Docker network and does not expose port `5432` externally.
