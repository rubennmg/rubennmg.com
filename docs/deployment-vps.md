# Two environments on one VPS

Both branches deploy complete Docker stacks: `develop` → `rubennmg.cloud`, `main` → `rubennmg.com`.
Docker Engine with Compose supporting `up --wait`, Git, Bash, `flock` (util-linux), curl and OpenSSL are required on a Linux VPS. There are no provider-specific services.

## Layout and isolation

| Component | Checkout / live config | Compose project | PostgreSQL volume |
| --- | --- | --- | --- |
| Staging | `/home/deploy/apps/rubennmg.com` (existing checkout) | `staging` | `staging_postgres_data` |
| Production | `/home/deploy/apps/rubennmg-production` (separate clone) | `rubennmg-production` | `rubennmg-production_postgres_data` |
| Shared Caddy | `/home/deploy/apps/rubennmg-proxy` (copied config) | `rubennmg-proxy` | none |

Each application project has frontend (Astro build served by Nginx), FastAPI and PostgreSQL 16. No Node runtime is needed. Only Caddy publishes TCP 80/443. SSH remains available for administration. Neither app publishes backend or database ports.

Caddy joins `rubennmg_staging_web` and `rubennmg_production_web`; application containers join only their own environment's web network. Each database joins only its project-specific `internal: true` network with its backend. The public `/api` prefix is preserved, not stripped. `/health` is also forwarded. `www` hosts work, and `api.rubennmg.cloud` is retained for old staging clients.

PostgreSQL volumes are external and explicitly named: deployments fail if a volume is absent, and Compose does not own its deletion. The historical staging project name and volume name are deliberately retained. Caddy likewise reuses the historical `staging_caddy_data` volume for certificates. Production starts with a new database; no staging records are copied automatically.

## GitHub configuration

Create/retain GitHub Environments **staging** and **production**. Configure these four secrets separately in **each** environment (the names are deliberately identical; the environment selects their values):

| Secret | Value |
| --- | --- |
| `VPS_HOST` | Same VPS IP/hostname for both environments |
| `VPS_USER` | `deploy` |
| `VPS_SSH_KEY` | Dedicated SSH private key authorized for that user; preferably a different key per environment |
| `VPS_KNOWN_HOSTS` | Verified OpenSSH known_hosts entry for the exact `VPS_HOST` |

Obtain the host fingerprint via the VPS console (`ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`), and verify it against the key you add to `VPS_KNOWN_HOSTS`. Do not trust an unverified scan during the workflow. Port 22 is assumed.

The VPS user needs Docker access and read access to the Git repository. This is separate from the Actions → VPS SSH key. For a private repository, configure a read-only repository deploy key on the VPS. Both clones must be able to `git fetch origin` unattended.

Remove the obsolete `PREMIUM_FTP_HOST`, `PREMIUM_FTP_USER`, `PREMIUM_FTP_PASSWORD`, `PREMIUM_FTP_TARGET_DIR` secrets. The FTP workflow is deleted. Production still creates its version tag/GitHub release, now only after successful VPS deployment; its job needs `contents: write`.

Both workflows run reusable CI first, deploy the exact verified SHA and skip superseded commits. Each has its own concurrency group. Remote checkout updates and deployments have environment-specific `flock` locks. Production never checks out code in the staging directory. Do not manually change a checkout while its deployment is running.

## DNS and firewall

For **both** `rubennmg.com` and `rubennmg.cloud`:

```text
A     @      VPS_IPV4
CNAME www    rubennmg.com.       # use rubennmg.cloud. in the cloud zone
```

An A record for `www` pointing directly at the same VPS is also valid. Retain/add `A api VPS_IPV4` only in the `rubennmg.cloud` zone for backward compatibility. Production requires no API subdomain.

Remove conflicting old web-hosting A/AAAA records. Only retain/add AAAA if this VPS has working public IPv6 with the same firewall access. Keep mail MX/TXT records. Any restrictive CAA records must allow Caddy's configured/default certificate issuer. Allow inbound TCP 80/443 and administrative SSH, including in a provider firewall if present. Caddy obtains and renews certificates automatically; persistent `/data` must survive updates.

## Environment files

Staging: `/home/deploy/apps/rubennmg.com/infra/staging/.env.staging`.
Production: `/home/deploy/apps/rubennmg-production/infra/production/.env.production`.

Use the environment-specific example files. All settings and their semantics are listed in [environment-variables.md](environment-variables.md). In particular:

- `PUBLIC_API_URL=` **must be empty for same-origin routing**. The frontend already appends `/api/...`; do not set this to `/api`. This is embedded during build.
- `CORS_ALLOWED_ORIGINS` contains only the environment's own root and www HTTPS origins.
- Set independent `POSTGRES_PASSWORD`, `ADMIN_PASSWORD` and `AUTH_SECRET_KEY`. Generate values with `openssl rand -hex 32`. The DB password is interpolated in a URL, so use URL-safe characters.
- Retain the **existing staging PostgreSQL password**. Changing this env setting does not rotate an initialized PostgreSQL role's password.
- `AUTH_COOKIE_NAME` should differ between environments, as in the examples. `AUTH_SESSION_DAYS=7`, `ENABLE_DEMO_DATA=false`.
- `APP_ENV`, database name/user and `DATABASE_URL` are fixed by each Compose configuration. An old `APP_ENV` entry in staging's env file has no effect.

Files are ignored by Git, excluded from image build contexts, and should have mode 600. The seed creates missing games/admin only; changing `ADMIN_PASSWORD` will not reset an existing admin password.

## First migration: existing staging VPS

Prepare this before enabling the new workflows on their respective branches. Temporarily disable deployment workflows in GitHub Actions during provisioning/merging, then re-enable them after the manual checks pass. The migration of Caddy requires a short interruption to HTTPS; normal deployments do not restart it. Commands below run as `deploy`, unless explicitly prefixed with sudo.

**Before updating the existing checkout**, identify the current resources and back up staging:

```bash
cd /home/deploy/apps/rubennmg.com/infra/staging
docker compose --env-file .env.staging -f compose.yml ps
old_db=$(docker compose --env-file .env.staging -f compose.yml ps -q db)
old_caddy=$(docker compose --env-file .env.staging -f compose.yml ps -q caddy)
test -n "$old_db" && test -n "$old_caddy"
docker inspect "$old_db" --format '{{range .Mounts}}{{println .Name .Destination}}{{end}}'
docker inspect "$old_caddy" --format '{{range .Mounts}}{{println .Name .Destination}}{{end}}'
umask 077
mkdir -p /home/deploy/backups/postgres
docker compose --env-file .env.staging -f compose.yml exec -T db pg_dump -U rubennmg -Fc rubennmg_staging > /home/deploy/backups/postgres/staging-before-vps-migration.dump
cp .env.staging /home/deploy/backups/staging-before-vps-migration.env
```

Confirm the DB mount is **`staging_postgres_data`** and Caddy `/data` is **`staging_caddy_data`**. If your existing Compose project name was overridden, stop here: the names in this repository must be adapted to the actual staging volumes before proceeding. Never create an empty replacement volume to bypass this check on an existing installation. Keep the backup off the VPS as well.

Update the checkout to a reviewed commit containing these changes (once merged to develop):

```bash
cd /home/deploy/apps/rubennmg.com
git fetch origin develop
git checkout --detach origin/develop
# Existing untracked .env.staging is retained.
chmod 600 infra/staging/.env.staging
nano infra/staging/.env.staging
# Set PUBLIC_API_URL=, staging-only CORS; retain existing DB password and secrets.

git clone --branch main git@github.com:rubennmg/rubennmg.com.git /home/deploy/apps/rubennmg-production
cd /home/deploy/apps/rubennmg-production
# main must also contain the reviewed new infrastructure before continuing.
umask 077
cp infra/production/.env.production.example infra/production/.env.production
nano infra/production/.env.production
chmod 600 infra/production/.env.production
```

Provision networks and **only the new production database volume**. These network commands also work if provisioned already:

```bash
docker network inspect rubennmg_staging_web >/dev/null 2>&1 || docker network create rubennmg_staging_web
docker network inspect rubennmg_production_web >/dev/null 2>&1 || docker network create rubennmg_production_web
docker volume inspect staging_postgres_data >/dev/null
docker volume inspect staging_caddy_data >/dev/null
docker volume create rubennmg-production_postgres_data

# Keep shared live proxy config outside both git checkouts.
mkdir -p /home/deploy/apps/rubennmg-proxy
cp /home/deploy/apps/rubennmg.com/infra/proxy/compose.yml /home/deploy/apps/rubennmg-proxy/compose.yml
cp /home/deploy/apps/rubennmg.com/infra/proxy/Caddyfile /home/deploy/apps/rubennmg-proxy/Caddyfile

docker compose -f /home/deploy/apps/rubennmg-proxy/compose.yml run --rm --no-deps caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile

# Build/migrate both applications before moving public traffic.
bash /home/deploy/apps/rubennmg-production/infra/production/deploy.sh --skip-public-checks
bash /home/deploy/apps/rubennmg.com/infra/staging/deploy.sh --skip-public-checks
```

The old Caddy may lose its old upstream connection while staging moves networks. Now replace just that container; PostgreSQL stays in place. Re-discover it by Compose labels if this is a new shell:

```bash
old_caddy=$(docker ps -aq --filter label=com.docker.compose.project=staging --filter label=com.docker.compose.service=caddy)
test -n "$old_caddy"
docker stop "$old_caddy"
docker rm "$old_caddy"
docker compose -f /home/deploy/apps/rubennmg-proxy/compose.yml up -d
```

No volume is removed. Copying the Caddy config outside Git prevents subsequent branch deployments from changing the shared live configuration. Point production DNS at this VPS when ready (lower TTL beforehand); existing staging DNS should already be correct. Test HTTPS below. If using `curl --resolve` before DNS propagation, TLS certificate issuance still requires publicly correct DNS/ACME reachability.

## Fresh VPS / future provider migration

Install Docker Engine and its Compose plugin for your Linux distribution, plus Git/curl/OpenSSL/util-linux. Create the deploy user and grant Docker access, then log in again:

```bash
sudo adduser deploy
sudo usermod -aG docker deploy
sudo -iu deploy
mkdir -p /home/deploy/apps
git clone --branch develop git@github.com:rubennmg/rubennmg.com.git /home/deploy/apps/rubennmg.com
git clone --branch main git@github.com:rubennmg/rubennmg.com.git /home/deploy/apps/rubennmg-production
umask 077
cp /home/deploy/apps/rubennmg.com/infra/staging/.env.staging.example /home/deploy/apps/rubennmg.com/infra/staging/.env.staging
cp /home/deploy/apps/rubennmg-production/infra/production/.env.production.example /home/deploy/apps/rubennmg-production/infra/production/.env.production
nano /home/deploy/apps/rubennmg.com/infra/staging/.env.staging
nano /home/deploy/apps/rubennmg-production/infra/production/.env.production

docker network create rubennmg_staging_web
docker network create rubennmg_production_web
# Only for a NEW installation (or intentionally provisioned restore target):
docker volume create staging_postgres_data
docker volume create rubennmg-production_postgres_data
docker volume create staging_caddy_data
mkdir -p /home/deploy/apps/rubennmg-proxy
cp /home/deploy/apps/rubennmg.com/infra/proxy/compose.yml /home/deploy/apps/rubennmg-proxy/compose.yml
cp /home/deploy/apps/rubennmg.com/infra/proxy/Caddyfile /home/deploy/apps/rubennmg-proxy/Caddyfile
bash /home/deploy/apps/rubennmg.com/infra/staging/deploy.sh --skip-public-checks
bash /home/deploy/apps/rubennmg-production/infra/production/deploy.sh --skip-public-checks
docker compose -f /home/deploy/apps/rubennmg-proxy/compose.yml up -d
```

For a provider migration with existing data, restore each environment's backup into its own database **before** running the deployment/migrations (see [operations.md](operations.md)); copy existing secrets too. Merely cloning the repository does not transfer databases. Update DNS and the two GitHub environments' VPS connection secrets/fingerprints.

## Verification and normal deployments

```bash
curl --fail https://rubennmg.cloud/games/ -o /dev/null
curl --fail https://rubennmg.cloud/api/health
curl --fail https://rubennmg.cloud/api/health/db
curl --fail https://rubennmg.com/games/ -o /dev/null
curl --fail https://rubennmg.com/api/health
curl --fail https://rubennmg.com/api/health/db
curl --fail https://api.rubennmg.cloud/api/health/db
# /api/health must report staging vs production respectively.

docker compose -p staging --env-file /home/deploy/apps/rubennmg.com/infra/staging/.env.staging -f /home/deploy/apps/rubennmg.com/infra/staging/compose.yml ps
docker compose -p rubennmg-production --env-file /home/deploy/apps/rubennmg-production/infra/production/.env.production -f /home/deploy/apps/rubennmg-production/infra/production/compose.yml ps
docker compose -f /home/deploy/apps/rubennmg-proxy/compose.yml logs --tail=100 caddy
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

Only the proxy should show host port bindings; `5432/tcp`, `8000/tcp`, `80/tcp` without a host address are image metadata, not published ports. Check login, CSRF-protected admin actions and rankings independently on both domains. Same-origin cookies may require logging in again after migrating from the staging API subdomain.

After bootstrapping, deploy manually with either command (or push the corresponding branch):

```bash
bash /home/deploy/apps/rubennmg.com/infra/staging/deploy.sh
bash /home/deploy/apps/rubennmg-production/infra/production/deploy.sh
```

Sequence: config validation → require volume/network → build → wait for DB → Alembic → seed missing records → start/wait for app healthchecks → schema/API checks → public HTTPS checks. Each script targets exactly `db backend frontend` in its own project, never the proxy or the other project. Healthchecks detect failed starts; they do not provide zero-downtime switching. Brief 502s can occur while a single backend/frontend is replaced. No automatic rollback is implemented.

You can verify isolation on the VPS by recording the other project's container IDs/StartedAt timestamps before and after a deployment; those should be unchanged. Repository tests check project/volume/network separation, deployment ordering, failure propagation, branch/checkout separation and absence of proxy/destructive cleanup calls.

No workflow runs `down`, volume deletion or global image/system pruning. Existing deployments had no automatic image cleanup; that remains the case. Plan capacity for two builds/stacks and manage disk use through operations. External volumes protect against Compose removal, not administrator deletion, destructive future Alembic migrations or VPS loss. Back up both databases; migrations must be reviewed and compatible with the previous running application version.
