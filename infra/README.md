# Infrastructure

- `local/compose.yml`: local development only; publishes development ports.
- `compose.app.yml`: shared frontend/backend/PostgreSQL definitions, extended by both VPS environments.
- `staging/compose.yml`: project `staging`, preserving the existing DB volume.
- `production/compose.yml`: project `rubennmg-production`, isolated database and networks.
- `proxy/`: shared Caddy template. Install separately from both Git checkouts; application deployments never update it.
- `deploy.sh`: shared build/migration/healthcheck sequence, selected by each environment's wrapper.
- `remote-deploy.sh`: exact-SHA checkout/deploy entry point invoked over SSH by Actions.
- `test_deploy.py`: deployment failure handling and isolation regression tests.

See [VPS deployment and migration](../docs/deployment-vps.md) for secrets, DNS, exact bootstrap commands and preservation of existing staging data/certificates.
