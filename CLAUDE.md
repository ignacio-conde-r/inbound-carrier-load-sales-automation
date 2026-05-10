# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Automation tooling for inbound carrier load sales. Early-stage Python project — no source files exist yet beyond `requirements.txt`.

## Environment Setup

```powershell
# Create and activate virtual environment (Windows)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Tech Stack (from requirements.txt)

| Layer | Library |
|---|---|
| API backend | FastAPI + uvicorn |
| Frontend / dashboard | Streamlit |
| Database ORM | SQLAlchemy 2.x (async) + aiosqlite |
| Migrations | Alembic |
| Config / validation | Pydantic v2 + pydantic-settings + python-dotenv |
| HTTP client | httpx + requests + tenacity (retries) |
| Data processing | pandas + numpy |
| Visualization | Plotly + Altair |
| Testing | pytest + pytest-asyncio |

## Expected Commands (once source exists)

```powershell
# Run FastAPI backend
uvicorn app.main:app --reload

# Run Streamlit frontend
streamlit run app/ui.py

# Run database migrations
alembic upgrade head

# Run tests
pytest

# Run a single test
pytest tests/test_foo.py::test_bar -v
```

## Key Conventions to Follow

- Use `pydantic-settings` with `python-dotenv` for all configuration (env vars via `.env` file).
- SQLAlchemy models should use the async engine (`aiosqlite`) with `async_sessionmaker`.
- Alembic manages all schema changes — never alter tables manually.
- Use `httpx.AsyncClient` with `tenacity` retry decorators for external HTTP calls.
- Tests are async-first (`pytest-asyncio`); mark async tests with `@pytest.mark.asyncio`.
