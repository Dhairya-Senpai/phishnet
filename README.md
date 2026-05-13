# Phishnet

A full-stack phishing analysis platform for red team and security operations workflows.
Inspect phishing email delivery, authentication results (SPF/DKIM/DMARC), and defensive bypass behavior through a unified dashboard.

## Stack

- **Backend:** FastAPI, Python 3.12, PostgreSQL, SQLAlchemy, Celery, Redis
- **Frontend:** React 18, TypeScript, Tailwind CSS, Recharts
- **Mail Infrastructure:** Postfix (SMTP ingestion on port 2525)
- **Deployment:** Docker Compose (local + production)

## Architecture

```
Internet/Test Script
        ↓ SMTP :2525
    Postfix
        ↓ pipe
  pipe_to_api.py
        ↓ POST /api/v1/emails/ingest
  FastAPI Backend ──→ PostgreSQL
        ↓
  Celery Workers (async analysis)
        ↓
  React Dashboard
```

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

- Frontend:  http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- SMTP ingestion: localhost:2525

## Testing Email Ingestion

**Option 1 — SMTP (Postfix)**
```bash
python3 scripts/send_test_email.py
```
Sends a sample phishing email directly to Postfix via SMTP. It will be automatically analyzed and appear in the dashboard.

**Option 2 — Manual paste (UI)**
Go to http://localhost:3000/ingest, click "Load sample phishing email", then hit Ingest & Analyze.

**Option 3 — API**
```bash
curl -X POST http://localhost:8000/api/v1/emails/ingest \
  -H "X-API-Key: change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{"raw_email": "From: test@evil.com\nTo: victim@target.com\nSubject: Test\n\nBody"}'
```

## Project Structure

```
phishnet/
├── backend/
│   └── app/
│       ├── api/routes/     # emails, campaigns, analytics
│       ├── core/           # config, security
│       ├── db/             # database session
│       ├── models/         # SQLAlchemy models
│       ├── schemas/        # Pydantic schemas
│       └── services/       # email_parser, ingestion
├── frontend/
│   └── src/
│       ├── pages/          # Dashboard, Emails, Campaigns, Ingest
│       ├── components/     # Layout, Sidebar
│       └── lib/            # API client
├── infrastructure/
│   ├── postfix/            # Postfix SMTP ingestion service
│   └── nginx/              # Production reverse proxy
├── scripts/
│   └── send_test_email.py  # SMTP test script
└── docker-compose.yml
```

## Environment Variables

See `.env.example` for all required variables. Key ones:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `API_KEY` | Backend API authentication key |
| `ALLOWED_ORIGINS` | CORS origins as JSON array e.g. `["http://localhost:3000"]` |
| `VITE_API_KEY` | Frontend API key (must match `API_KEY`) |
| `VITE_API_URL` | Backend URL for Docker networking e.g. `http://backend:8000` |

## Development (without Docker)

```bash
# Backend
cd backend
python -m venv venv
venv/Scripts/activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Tests
cd backend
pytest tests/ -v
```

## Production

```bash
docker compose --profile production up --build
```

Adds Nginx reverse proxy on port 80 routing `/api` to backend and `/` to frontend.