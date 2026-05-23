# Operations

Operational commands assume the VPS repository path is:

```txt
/home/deploy/apps/rubennmg.com
```

## Staging Stack

Run commands from `infra/staging`:

```bash
cd /home/deploy/apps/rubennmg.com/infra/staging
```

Start or update staging:

```bash
docker compose --env-file .env.staging -f compose.yml up -d --build
```

Stop staging:

```bash
docker compose --env-file .env.staging -f compose.yml down
```

Show service status:

```bash
docker compose --env-file .env.staging -f compose.yml ps
```

## Logs

```bash
docker compose --env-file .env.staging -f compose.yml logs -f caddy
docker compose --env-file .env.staging -f compose.yml logs -f frontend
docker compose --env-file .env.staging -f compose.yml logs -f backend
docker compose --env-file .env.staging -f compose.yml logs -f db
```

## Rebuild One Service

```bash
docker compose --env-file .env.staging -f compose.yml up -d --build backend
docker compose --env-file .env.staging -f compose.yml up -d --build frontend
```

## Health Checks

```bash
curl https://api.rubennmg.cloud/health
curl https://api.rubennmg.cloud/api/health/db
```

From inside the backend container:

```bash
docker compose --env-file .env.staging -f compose.yml exec backend python -c "import json, urllib.request; print(json.load(urllib.request.urlopen('http://127.0.0.1:8000/api/health/db')))"
```

## PostgreSQL Backup

Recommended VPS backup directory:

```txt
/home/deploy/backups/postgres
```

Create a manual backup:

```bash
mkdir -p /home/deploy/backups/postgres
docker compose --env-file .env.staging -f compose.yml exec -T db pg_dump -U rubennmg rubennmg_staging > /home/deploy/backups/postgres/backup_$(date +%F).sql
```

## PostgreSQL Restore

Restore from a backup file:

```bash
docker compose --env-file .env.staging -f compose.yml exec -T db psql -U rubennmg rubennmg_staging < /home/deploy/backups/postgres/backup_YYYY-MM-DD.sql
```

Only restore after confirming the target database can be overwritten.

## Caddy

Reload the stack after changing `Caddyfile`:

```bash
docker compose --env-file .env.staging -f compose.yml up -d caddy
```

Check Caddy logs:

```bash
docker compose --env-file .env.staging -f compose.yml logs -f caddy
```

## Cleanup

Remove unused Docker images:

```bash
docker image prune -f
```
