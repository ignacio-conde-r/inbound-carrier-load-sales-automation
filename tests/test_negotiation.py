import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

API_KEY = "hr-backend-key-2026-ignacio"
HEADERS = {"X-API-Key": API_KEY}


@pytest.mark.asyncio
async def test_negotiation_accept():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/negotiations/evaluate", json={
            "call_id": "test-call-001",
            "load_id": "L-1001",
            "carrier_mc_number": "MC-123456",
            "round_number": 1,
            "carrier_offer": 2500.0,
        }, headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["decision"] == "accept"


@pytest.mark.asyncio
async def test_negotiation_counter():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/negotiations/evaluate", json={
            "call_id": "test-call-002",
            "load_id": "L-1001",
            "carrier_mc_number": "MC-123456",
            "round_number": 1,
            "carrier_offer": 9999.0,
        }, headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["decision"] == "counter"


@pytest.mark.asyncio
async def test_negotiation_reject_round3():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/negotiations/evaluate", json={
            "call_id": "test-call-003",
            "load_id": "L-1001",
            "carrier_mc_number": "MC-123456",
            "round_number": 3,
            "carrier_offer": 9999.0,
        }, headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["decision"] == "reject"


@pytest.mark.asyncio
async def test_call_log():
    import uuid
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/calls/log", json={
            "call_id": f"test-call-log-{uuid.uuid4().hex[:8]}",
            "carrier_mc_number": "MC-123456",
            "carrier_name": "Test Carrier LLC",
            "selected_load_id": "L-1001",
            "final_offer": 2500.0,
            "outcome": "booked",
            "sentiment": "positive",
            "transcript_summary": "Carrier agreed to haul Chicago to Dallas at $2,500.",
        }, headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["success"] == True
