# HappyRobot Inbound Carrier Sales API

## Overview

FastAPI backend powering HappyRobot's inbound carrier sales automation workflow for a freight brokerage. The HappyRobot voice agent calls this API as tool endpoints during live carrier calls to verify carriers against FMCSA records, search and score available loads, negotiate pricing within authorized margins, log call outcomes and sentiment, and serve operational metrics to a real-time Streamlit dashboard.

## Architecture

```
Carrier Web Call
→ HappyRobot Voice Agent
→ POST /carriers/verify       (FMCSA eligibility check)
→ POST /loads/search          (load matching & scoring)
→ POST /negotiations/evaluate (pricing policy engine)
→ POST /calls/log             (outcome & sentiment logging)
→ GET  /metrics/*             (dashboard data)
→ Streamlit Operations Dashboard
```

## Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /health | No | Health check |
| POST | /carriers/verify | X-API-Key | FMCSA carrier eligibility |
| POST | /loads/search | X-API-Key | Load matching with scoring |
| POST | /negotiations/evaluate | X-API-Key | Pricing policy engine |
| POST | /calls/log | X-API-Key | Call outcome logging |
| GET | /metrics/summary | X-API-Key | KPI summary |
| GET | /metrics/calls | X-API-Key | Recent calls |
| GET | /metrics/negotiations | X-API-Key | Negotiation events |

## Pricing Policy

- Short haul ≤300 miles: max +5% above listed rate
- Mid haul 301–900 miles: max +8%
- Long haul >900 miles: max +10%
- Reefer equipment: +2% additional tolerance
- Pickup within 24 hours: +3% urgency bonus
- Heavy loads >42,000 lbs: capped at 5%
- Max 3 negotiation rounds enforced server-side

## Quick Start

### Local

```bash
cp .env.example .env
python scripts/seed_db.py
uvicorn app.main:app --reload
# In second terminal:
streamlit run dashboard/streamlit_app.py
```

### Docker

```bash
docker compose up --build
# API:       http://localhost:8000
# Dashboard: http://localhost:8501
# Docs:      http://localhost:8000/docs
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| API_KEY | X-API-Key for all protected endpoints | required |
| DATABASE_URL | SQLite async URL | sqlite+aiosqlite:///./data/happyrobot.db |
| FMCSA_MODE | mock or live | mock |
| FMCSA_WEBKEY | FMCSA QCMobile API key | — |

## Testing

```bash
pytest -v                          # 20 unit tests
python scripts/smoke_test.py       # 16 end-to-end checks (requires uvicorn running)
```

## Stack

Python 3.11 · FastAPI · Pydantic v2 · SQLAlchemy 2.0 async · aiosqlite · SQLite · Streamlit · Plotly · Docker
