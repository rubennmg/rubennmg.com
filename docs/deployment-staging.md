# Staging Deployment

`develop` deploys the complete staging stack to `https://rubennmg.cloud` on the shared VPS. API calls use `/api`; `api.rubennmg.cloud` remains available for compatibility.

Follow [the VPS deployment guide](deployment-vps.md), including the existing-staging migration procedure before using the new workflow. The existing checkout and `infra/staging/.env.staging` are retained.

Normal deployment after provisioning:

```bash
bash /home/deploy/apps/rubennmg.com/infra/staging/deploy.sh
```

The workflow uses GitHub Environment `staging`, with `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `VPS_KNOWN_HOSTS`. It runs CI first and deploys only the verified develop SHA.
