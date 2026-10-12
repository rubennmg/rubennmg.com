# VPS Operations

Provisioning/migration: [deployment-vps.md](deployment-vps.md). Commands run as `deploy`. Select **one** environment explicitly in your shell:

```bash
# Staging:
cd /home/deploy/apps/rubennmg.com/infra/staging
compose=(docker compose -p staging --env-file .env.staging -f compose.yml)
database=rubennmg_staging

# OR production, in its own checkout:
cd /home/deploy/apps/rubennmg-production/infra/production
compose=(docker compose -p rubennmg-production --env-file .env.production -f compose.yml)
database=rubennmg_production
```

Status and logs:

```bash
"${compose[@]}" ps
"${compose[@]}" logs --tail=100 backend frontend db
```

Deploy using the environment wrapper (`bash deploy.sh` from that environment directory). It builds, runs migrations and seed, starts services, waits for healthchecks and verifies HTTPS. Do not bypass migrations with an ad-hoc `up --build`.

## Backups and restore

Back up each database separately and store encrypted copies off the VPS:

```bash
umask 077
mkdir -p /home/deploy/backups/postgres
"${compose[@]}" exec -T db pg_dump -U rubennmg -Fc "$database" > "/home/deploy/backups/postgres/${database}_$(date +%F_%H%M%S).dump"
```

For a **fresh, empty restore target** (after creating its external volume/network and env file), start only its database and restore the selected dump before the first normal deployment:

```bash
"${compose[@]}" up -d --wait db
# Set this to the correct environment's actual backup file.
backup_file=/home/deploy/backups/postgres/REPLACE_WITH_CORRECT_BACKUP.dump
"${compose[@]}" exec -T db pg_restore --exit-on-error --no-owner -U rubennmg -d "$database" < "$backup_file"
bash deploy.sh --skip-public-checks
```

Restoring into an existing nonempty database needs an explicit reviewed recovery plan; do not run a destructive restore blindly. Test backup restoration periodically. Reverting application code does not revert schema migrations; keep migrations backward compatible and review all schema changes.

## Shared Caddy

Live configuration is `/home/deploy/apps/rubennmg-proxy`, separate from Git checkouts. Both branches carry the template but neither application workflow copies or reloads it. Apply intended proxy changes manually and review their effect on both domains:

```bash
cd /home/deploy/apps/rubennmg-proxy
# Edit the live Caddyfile in place, then:
docker compose -f compose.yml exec -T caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
docker compose -f compose.yml exec -T caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
docker compose -f compose.yml logs --tail=100 caddy
```

If replacing the bind-mounted file via an atomic rename, the running container can retain the old inode. Edit in place (for example `cat reviewed-Caddyfile > Caddyfile`) or deliberately recreate the proxy during a maintenance window.

## Disk usage

```bash
docker system df
docker image ls --filter dangling=true
```

There is no automatic global prune, since both environments share the daemon. When no builds/deployments are running, inspect and remove only individually selected unused image IDs with `docker image rm IMAGE_ID` (without force). Never prune volumes or run `down -v` as a deployment/cleanup step. Keep enough disk space for two stacks and image builds.

## Check deployment isolation

Record the other project's running containers before a deploy, then compare afterward:

```bash
# Example: verify production did not restart while deploying staging.
for id in $(docker ps -q --filter label=com.docker.compose.project=rubennmg-production); do
  docker inspect "$id" --format '{{.Id}} {{.State.StartedAt}}'
done > /tmp/production-before.txt
bash /home/deploy/apps/rubennmg.com/infra/staging/deploy.sh
for id in $(docker ps -q --filter label=com.docker.compose.project=rubennmg-production); do
  docker inspect "$id" --format '{{.Id}} {{.State.StartedAt}}'
done > /tmp/production-after.txt
diff -u /tmp/production-before.txt /tmp/production-after.txt
```

Repeat in reverse with project `staging` and the production deploy script. No diff is expected. Check both `/api/health` endpoints report their correct environment and `/api/health/db` succeeds.
