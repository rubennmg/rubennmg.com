#!/usr/bin/env bash
set -euo pipefail

case "${1:-}" in
  staging) project=staging; domain=rubennmg.cloud ;;
  production) project=rubennmg-production; domain=rubennmg.com ;;
  *) echo "Usage: $0 staging|production [--skip-public-checks]" >&2; exit 1 ;;
esac
environment="$1"
[[ $# == 1 || ( $# == 2 && "$2" == --skip-public-checks ) ]] || exit 1
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/$environment"
test -f ".env.$environment" || { echo "Missing infra/$environment/.env.$environment" >&2; exit 1; }

# Also serializes manual deploys with CI for this environment.
exec 9>"/tmp/rubennmg-$environment-deploy.lock"
flock 9
compose=(docker compose -p "$project" --env-file ".env.$environment" -f compose.yml)
"${compose[@]}" config --quiet

# External volumes must be provisioned explicitly. Never silently replace a missing DB.
docker volume inspect "${project}_postgres_data" >/dev/null
docker network inspect "rubennmg_${environment}_web" >/dev/null
"${compose[@]}" build --pull backend frontend
"${compose[@]}" up -d --wait --wait-timeout 120 db
"${compose[@]}" run --rm --no-deps backend alembic upgrade head
"${compose[@]}" run --rm --no-deps backend python -m app.scripts.seed --missing-only
"${compose[@]}" up -d --wait --wait-timeout 180 db backend frontend

"${compose[@]}" exec -T backend python -c '
import json
import urllib.request
def read(path):
    with urllib.request.urlopen("http://127.0.0.1:8000" + path, timeout=10) as response:
        data = json.load(response)
    print("OK", path)
    return data
read("/api/health/db")
for game in read("/api/games"):
    read("/api/games/" + game["slug"] + "/rankings")
'
if [[ "${2:-}" != --skip-public-checks ]]; then
  for path in /games/ /api/health/db; do
    curl --fail --silent --show-error --retry 6 --retry-delay 5 --retry-all-errors --max-time 15 "https://$domain$path" -o /dev/null
  done
  echo "$environment deployment verified."
else
  echo "$environment services ready; public HTTPS checks still required."
fi
