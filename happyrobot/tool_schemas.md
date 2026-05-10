# HappyRobot Tool Schemas

## Tool 1: Verify Carrier

- **URL**: POST `{API_BASE}/carriers/verify`
- **Headers**: `X-API-Key: {API_KEY}`
- **Input**:
```json
{"mc_number": "{{mc_number}}", "caller_phone": "{{caller_phone}}"}
```
- **Key outputs used by agent**: `eligible`, `authority_status`, `legal_name`, `reason`

---

## Tool 2: Search Loads

- **URL**: POST `{API_BASE}/loads/search`
- **Headers**: `X-API-Key: {API_KEY}`
- **Input**:
```json
{"origin": "{{origin}}", "destination": "{{destination}}", "equipment_type": "{{equipment_type}}"}
```
- **Key outputs used by agent**: `matches_found`, `recommended_load.pitch_summary`, `recommended_load.load_id`, `recommended_load.loadboard_rate`

---

## Tool 3: Evaluate Negotiation Offer

- **URL**: POST `{API_BASE}/negotiations/evaluate`
- **Headers**: `X-API-Key: {API_KEY}`
- **Input**:
```json
{"call_id": "{{call_id}}", "load_id": "{{load_id}}", "carrier_mc_number": "{{mc_number}}", "round_number": {{round_number}}, "carrier_offer": {{carrier_offer}}}
```
- **Key outputs used by agent**: `decision`, `agreed_price`, `counter_offer`, `agent_message`

---

## Webhook: Log Call

- **URL**: POST `{API_BASE}/calls/log`
- **Headers**: `X-API-Key: {API_KEY}`
- **Input**:
```json
{"call_id": "{{call_id}}", "happyrobot_run_id": "{{run_id}}", "carrier_mc_number": "{{mc_number}}", "carrier_name": "{{carrier_name}}", "selected_load_id": "{{load_id}}", "final_offer": {{final_offer}}, "outcome": "{{outcome}}", "sentiment": "{{sentiment}}", "transcript_summary": "{{summary}}"}
```
