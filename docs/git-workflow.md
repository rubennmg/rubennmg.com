# Git Workflow

This repository uses a reduced Gitflow.

## Branches

- `main`: current production branch for `rubennmg.com` on Premium Web Hosting.
- `develop`: staging branch for `rubennmg.cloud` on the VPS.
- `feature/*`: normal implementation work.
- `hotfix/*`: urgent production fixes based on `main`.

## Normal Flow

```txt
feature/* -> pull request -> develop -> staging deploy
develop -> pull request -> main -> production deploy
```

All feature work should start from `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-change
```

## Pull Requests

Open PRs from `feature/*` into `develop`.

After a PR into `develop` is merged, `.github/workflows/delete-merged-feature-branches.yml` deletes same-repository remote branches named `feature/*`.

Open PRs from `develop` into `main` when staging has been validated and production should be updated.

## Conventional Commits

Use short Conventional Commit messages:

```txt
feat: add backend foundation
infra: add staging compose stack
ci: add staging deployment workflow
docs: document VPS deployment
fix: correct production build path
```

## Hotfixes

For urgent production fixes:

```bash
git checkout main
git pull origin main
git checkout -b hotfix/short-description
```

Open the hotfix PR into `main`. After it is merged, backport or merge `main` into `develop` so staging stays aligned.
