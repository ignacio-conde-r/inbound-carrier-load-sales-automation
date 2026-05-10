import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

API_KEY = "hr-backend-key-2026-ignacio"
HEADERS = {"X-API-Key": API_KEY}


@pytest.mark.asyncio
async def test_verify_eligible_carrier():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/carriers/verify", json={"mc_number": "MC-123456"}, headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert data["eligible"] == True
    assert data["authority_status"] == "active"


@pytest.mark.asyncio
async def test_verify_ineligible_carrier():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/carriers/verify", json={"mc_number": "INACTIVE-999"}, headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert data["eligible"] == False


@pytest.mark.asyncio
async def test_verify_unknown_carrier():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/carriers/verify", json={"mc_number": "BADFORMAT"}, headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["authority_status"] == "not_found"
