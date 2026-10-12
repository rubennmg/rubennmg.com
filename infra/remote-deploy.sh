#!/usr/bin/env bash
set -euo pipefail
# Called through SSH from a workflow; each checkout has its own update lock.
case "${1:-}" in
  staging) branch=develop; checkout=/home/deploy/apps/rubennmg.com ;;
  production) branch=main; checkout=/home/deploy/apps/rubennmg-production ;;
  *) exit 1 ;;
esac
environment="$1"
deploy_sha="${2:-}"
[[ "$deploy_sha" =~ ^[0-9a-f]{40}$ ]] || exit 1
exec 8>"/tmp/rubennmg-$environment-checkout.lock"
flock 8
cd "$checkout"
git fetch origin "$branch"
if [[ "$(git rev-parse FETCH_HEAD)" != "$deploy_sha" ]]; then
  echo "Skipping superseded $environment commit."
  exit 0
fi
git checkout --detach "$deploy_sha"
git reset --hard "$deploy_sha"
bash "infra/$environment/deploy.sh"
echo "DEPLOYED_SHA=$deploy_sha"
