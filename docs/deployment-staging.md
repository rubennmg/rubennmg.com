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

The staging environment file must live at:

```txt
/home/deploy/apps/rubennmg.com/infra/staging/.env.staging
```

Create it from the root example:

```bash
cd /home/deploy/apps/rubennmg.com/infra/staging
cp ../../.env.example .env.staging
```

Then replace `POSTGRES_PASSWORD` with a real secret.

## Start Staging

From `infra/staging`:

```bash
docker compose --env-file .env.staging -f compose.yml up -d --build
```

## Check Services

```bash
docker compose --env-file .env.staging -f compose.yml ps
docker compose --env-file .env.staging -f compose.yml logs -f caddy
docker compose --env-file .env.staging -f compose.yml logs -f backend
```

Expected public checks once DNS points to the VPS:

```txt
https://rubennmg.cloud
https://api.rubennmg.cloud/health
```

PostgreSQL is only attached to the internal Docker network and does not expose port `5432` externally.
