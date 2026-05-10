import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

API_KEY = "hr-backend-key-2026-ignacio"
HEADERS = {"X-API-Key": API_KEY}


@pytest.mark.asyncio
async def test_metrics_summary():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/metrics/summary", headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert "total_calls" in data
    assert "booking_rate" in data


@pytest.mark.asyncio
async def test_metrics_calls():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/metrics/calls", headers=HEADERS)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_metrics_negotiations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/metrics/negotiations", headers=HEADERS)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
