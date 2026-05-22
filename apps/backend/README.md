# rubennmg API

Minimal FastAPI backend prepared for the future full-stack application.

## Local Development

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

Available endpoints:

- `GET /health`
- `GET /api/health`
- `GET /api/health/db`

The database endpoint expects `DATABASE_URL` to point to a reachable PostgreSQL instance.
