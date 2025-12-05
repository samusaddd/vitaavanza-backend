# VitaAvanza Backend PRO (Pilot-Ready)

This is the **heavy**, production-style backend for the VitaAvanza pilot.

## Features

- FastAPI with modular routers
- PostgreSQL (Render) via SQLAlchemy 2.0
- Structured logging with Loguru
- JWT auth (user / admin / institution-ready)
- Weighted DVI engine (finance, logistics, health, education, wellbeing)
- Mitra AI assistant using OpenAI Chat Completions
- Opportunities API (create + list with min DVI filter)
- CORS config via env var
- Healthcheck + per-request latency logging

## Local setup

```bash
pip install -r requirements.txt
cp .env.example .env  # then edit values
uvicorn app.main:app --reload
```

## Important env vars

- `DATABASE_URL` — your Render PostgreSQL connection
- `SECRET_KEY` — long random string
- `OPENAI_API_KEY` — from OpenAI dashboard
- `ALLOWED_ORIGINS` — comma-separated frontend URLs

## Render start command

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
