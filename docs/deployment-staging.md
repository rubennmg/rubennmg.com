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

Then replace `POSTGRES_PASSWORD` with a real secret.

## GitHub Actions Deploy

Staging deploy runs automatically on every push to `develop` through `.github/workflows/deploy-staging.yml`.

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

The workflow connects by SSH and runs:

```bash
cd /home/deploy/apps/rubennmg.com
git fetch origin
git checkout develop
git pull origin develop
cd infra/staging
docker compose --env-file .env.staging -f compose.yml up -d --build
docker image prune -f
```

The file `infra/staging/.env.staging` must already exist on the VPS before the first automatic deployment.

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
