import requests, sys, json

BASE = "http://localhost:8000"
KEY = "hr-backend-key-2026-ignacio"
H = {"X-API-Key": KEY}
PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  ✅ {name}")
        PASS += 1
    else:
        print(f"  ❌ {name} {detail}")
        FAIL += 1


print("\n🔍 HappyRobot Backend Smoke Test\n")

print("1. Health")
r = requests.get(f"{BASE}/health")
check("GET /health 200", r.status_code == 200)
check("status=ok", r.json().get("status") == "ok")

print("\n2. Auth")
r = requests.post(f"{BASE}/carriers/verify", json={"mc_number": "MC-1"})
check("No key → 403", r.status_code == 403)

print("\n3. Carrier Verify")
r = requests.post(f"{BASE}/carriers/verify", json={"mc_number": "MC-123456"}, headers=H)
check("MC-123456 → eligible", r.status_code == 200 and r.json().get("eligible") == True)
r = requests.post(f"{BASE}/carriers/verify", json={"mc_number": "INACTIVE-999"}, headers=H)
check("INACTIVE-999 → not eligible", r.status_code == 200 and r.json().get("eligible") == False)

print("\n4. Load Search")
r = requests.post(f"{BASE}/loads/search", json={}, headers=H)
check("Empty search → matches found", r.status_code == 200 and r.json().get("matches_found") == True)
r = requests.post(f"{BASE}/loads/search", json={"equipment_type": "Reefer"}, headers=H)
check("Reefer filter → Reefer result", r.status_code == 200 and r.json()["recommended_load"]["equipment_type"] == "Reefer")
r = requests.post(f"{BASE}/loads/search", json={"origin": "Chicago"}, headers=H)
check("Chicago origin → match found", r.status_code == 200 and r.json().get("matches_found") == True)

print("\n5. Negotiation")
r = requests.post(f"{BASE}/negotiations/evaluate", json={
    "call_id": "smoke-001", "load_id": "L-1001", "carrier_mc_number": "MC-123",
    "round_number": 1, "carrier_offer": 2500.0
}, headers=H)
check("Round 1 low offer → accept", r.status_code == 200 and r.json().get("decision") == "accept")
r = requests.post(f"{BASE}/negotiations/evaluate", json={
    "call_id": "smoke-002", "load_id": "L-1001", "carrier_mc_number": "MC-123",
    "round_number": 1, "carrier_offer": 9999.0
}, headers=H)
check("Round 1 high offer → counter", r.status_code == 200 and r.json().get("decision") == "counter")
r = requests.post(f"{BASE}/negotiations/evaluate", json={
    "call_id": "smoke-003", "load_id": "L-1001", "carrier_mc_number": "MC-123",
    "round_number": 3, "carrier_offer": 9999.0
}, headers=H)
check("Round 3 high offer → reject", r.status_code == 200 and r.json().get("decision") == "reject")

print("\n6. Call Logging")
import uuid
r = requests.post(f"{BASE}/calls/log", json={
    "call_id": f"smoke-log-{uuid.uuid4().hex[:8]}",
    "carrier_mc_number": "MC-123456",
    "carrier_name": "Smoke Test Carrier LLC",
    "selected_load_id": "L-1001",
    "final_offer": 2500.0,
    "outcome": "booked",
    "sentiment": "positive",
    "transcript_summary": "Smoke test call log.",
}, headers=H)
check("POST /calls/log → success", r.status_code == 200 and r.json().get("success") == True)

print("\n7. Metrics")
r = requests.get(f"{BASE}/metrics/summary", headers=H)
check("GET /metrics/summary 200", r.status_code == 200)
check("total_calls >= 1", r.json().get("total_calls", 0) >= 1)
r = requests.get(f"{BASE}/metrics/calls", headers=H)
check("GET /metrics/calls is list", r.status_code == 200 and isinstance(r.json(), list))
r = requests.get(f"{BASE}/metrics/negotiations", headers=H)
check("GET /metrics/negotiations is list", r.status_code == 200 and isinstance(r.json(), list))

print(f"\n{'='*40}")
print(f"  Results: {PASS} passed, {FAIL} failed")
print(f"{'='*40}\n")
sys.exit(0 if FAIL == 0 else 1)
