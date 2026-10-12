# Production Deployment

`main` deploys frontend, FastAPI and an independent PostgreSQL database to `https://rubennmg.com` on the same VPS as staging. API calls use `/api` on the production domain.

Follow [the VPS deployment guide](deployment-vps.md) for the new checkout, secrets, DNS and initial provisioning. No FTP/Premium Hosting deployment remains. Version tags and GitHub releases are still created after a successful production deployment.

Normal deployment after provisioning:

```bash
bash /home/deploy/apps/rubennmg-production/infra/production/deploy.sh
```

The workflow uses GitHub Environment `production`, with `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `VPS_KNOWN_HOSTS`. It runs CI first and deploys only the verified main SHA.
