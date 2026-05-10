import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

API_KEY = "hr-backend-key-2026-ignacio"
HEADERS = {"X-API-Key": API_KEY}


@pytest.mark.asyncio
async def test_search_loads_no_filters():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/loads/search", json={}, headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert data["matches_found"] == True
    assert data["recommended_load"] is not None


@pytest.mark.asyncio
async def test_search_loads_by_equipment():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/loads/search", json={"equipment_type": "Reefer"}, headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert data["matches_found"] == True
    assert data["recommended_load"]["equipment_type"] == "Reefer"


@pytest.mark.asyncio
async def test_search_loads_no_match():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/loads/search", json={"origin": "Timbuktu"}, headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["matches_found"] == False
