# Production Premium Deployment

Production currently serves only the static Astro frontend from Hostinger Premium Web Hosting.

The backend, PostgreSQL and Caddy staging stack are not deployed to production in this phase.

## Trigger

Production deploy runs from `.github/workflows/deploy-production-premium.yml` on every push to `main`.

The workflow uses the GitHub environment `production`. Configure required reviewers on that environment if deployment approval should be manual.

## Build

The workflow builds the frontend from `apps/frontend`:

```bash
cd apps/frontend
npm ci
npm run build
```

The generated files in `apps/frontend/dist/` are uploaded to the Premium Hosting target directory.

## Required Secrets

Create these secrets in the GitHub `production` environment:

```txt
PREMIUM_FTP_HOST
PREMIUM_FTP_USER
PREMIUM_FTP_PASSWORD
PREMIUM_FTP_TARGET_DIR
```

Expected values:

```txt
PREMIUM_FTP_HOST=FTP/SFTP host from Hostinger
PREMIUM_FTP_USER=FTP user
PREMIUM_FTP_PASSWORD=FTP password
PREMIUM_FTP_TARGET_DIR=remote directory for rubennmg.com public files
```

`PREMIUM_FTP_TARGET_DIR` should usually point to the website public directory, for example `/public_html/`. Confirm the exact path in Hostinger before enabling the workflow.

## Rollback

The simplest rollback is to redeploy a previous known-good commit from `main`:

```bash
git checkout main
git revert COMMIT_SHA
git push origin main
```

For an urgent manual rollback, build a known-good commit locally and upload its `apps/frontend/dist/` contents with the Hostinger file manager or FTP client.

## Notes

- This workflow must not touch VPS services.
- This workflow must not deploy backend code.
- Keep real FTP credentials only in GitHub environment secrets.
