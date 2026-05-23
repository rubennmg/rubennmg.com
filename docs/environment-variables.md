# Environment Variables

## Public Variables

- `PUBLIC_API_URL`: frontend-visible API URL. Staging uses `https://api.rubennmg.cloud`.

## Backend Variables

- `APP_ENV`: runtime environment name, for example `staging`.
- `CORS_ALLOWED_ORIGINS`: comma-separated list of allowed frontend origins.
- `DATABASE_URL`: SQLAlchemy database URL. In staging it is composed inside Docker Compose from `POSTGRES_PASSWORD`.

## Database Variables

- `POSTGRES_PASSWORD`: PostgreSQL password. This is sensitive and must not be committed with a real value.

## Files

- `.env.example`: committed template with safe placeholder values.
- `infra/staging/.env.staging`: real staging values on the VPS, ignored by Git.

Never commit real `.env`, `.env.production` or `.env.staging` files.

## GitHub Actions Secrets

The `staging` environment requires:

- `VPS_HOST`: VPS hostname or IP address.
- `VPS_USER`: SSH user, expected to be `deploy`.
- `VPS_SSH_KEY`: private SSH key used by GitHub Actions to connect to the VPS.

Do not reuse a personal SSH key. Create a dedicated key for staging deployments.
