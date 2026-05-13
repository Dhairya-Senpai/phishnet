# Phishnet

A full-stack phishing analysis platform for red team and security operations workflows.
Inspect phishing email delivery, authentication results (SPF/DKIM/DMARC), and defensive bypass behavior through a unified dashboard.

## Stack

- **Backend:** FastAPI, Python 3.12, PostgreSQL, SQLAlchemy, Celery, Redis
- **Frontend:** React 18, TypeScript, Tailwind CSS, Recharts
- **Mail Infrastructure:** Postfix (email ingestion)
- **Deployment:** Docker Compose (local + production)

## Architecture

```
Internet → Postfix (SMTP) → Milter/Pipe → FastAPI Backend → PostgreSQL
                                                  ↓
                                            Celery Workers (async analysis)
                                                  ↓
                                          React Dashboard
```

## Quick Start (Local)

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
phishnet/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # Route handlers
│   │   ├── core/     # Config, security
│   │   ├── db/       # Database session
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # Business logic
│   └── tests/
├── frontend/         # React dashboard
├── infrastructure/   # Docker, Nginx configs
└── scripts/          # Utility scripts
```

## Environment Variables

See `.env.example` for all required variables.

## Development

```bash
# Backend only
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend only
cd frontend
npm install
npm run dev
```
