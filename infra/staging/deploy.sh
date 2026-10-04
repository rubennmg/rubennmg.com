#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
compose=(docker compose --env-file .env.staging -f compose.yml)
test -f .env.staging || { echo "Missing infra/staging/.env.staging" >&2; exit 1; }
"${compose[@]}" config --quiet

# Build before touching running services. Never remove database volumes.
"${compose[@]}" build --pull backend frontend
"${compose[@]}" up -d --wait --wait-timeout 120 db
"${compose[@]}" run --rm --no-deps backend alembic upgrade head
"${compose[@]}" run --rm --no-deps backend python -m app.scripts.seed --missing-only
"${compose[@]}" up -d --wait --wait-timeout 180

# Exercise the real schema as well as the database connection.
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
curl --fail --silent --show-error --retry 6 --retry-delay 5 --retry-all-errors --max-time 15 https://rubennmg.cloud/games/ -o /dev/null
curl --fail --silent --show-error --retry 6 --retry-delay 5 --retry-all-errors --max-time 15 https://api.rubennmg.cloud/api/health/db -o /dev/null
echo "Staging deployment verified."
