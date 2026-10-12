# Architecture

Both environments run on one provider-independent Linux VPS:

```text
Internet → shared Caddy (80/443, automatic TLS)
  rubennmg.com       → production frontend / backend → production PostgreSQL
  rubennmg.cloud     → staging frontend / backend    → staging PostgreSQL
```

Astro builds static files served by Nginx. `/api` and `/health` go to the matching FastAPI backend without rewriting the path. Each backend sees only its own PostgreSQL through its private Docker network. The proxy connects to two separate environment web networks. No app service publishes host ports.

Each branch has a separate checkout and Compose project. PostgreSQL data lives in distinct external volumes. Secrets remain in per-environment ignored files. A third project runs Caddy with persistent certificate storage and live configuration outside both Git checkouts. Application CI/CD does not restart or reconfigure it.

- `develop` → CI → SSH → `staging` → `rubennmg.cloud`.
- `main` → CI → SSH → `rubennmg-production` → `rubennmg.com` → GitHub release.

The legacy `api.rubennmg.cloud` route remains available, but new frontends use same-origin API URLs. Production has no dependency on FTP or Premium Hosting.

See [deployment-vps.md](deployment-vps.md) for resource names, migration and provisioning, and [board-games-rankings.md](board-games-rankings.md) for application features.
