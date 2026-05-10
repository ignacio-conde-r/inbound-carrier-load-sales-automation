# Test Call Scripts

## Script 1: Happy Path — Accept Listed Rate

- **Carrier MC**: MC-123456
- **Lane request**: Chicago to Dallas, Dry Van
- **Response to load pitch**: "That works, I'll take it at your listed rate"
- **Expected flow**:
  - `/carriers/verify` → eligible: true, authority_status: active
  - `/loads/search` → L-1001 matched and pitched
  - `/negotiations/evaluate` round 1, offer at or below listed rate → decision: accept
  - `/calls/log` → outcome: booked, sentiment: positive

---

## Script 2: Negotiation Path — Counter Then Agree

- **Carrier MC**: MC-789012
- **Lane**: Chicago to Houston, Reefer
- **First counter**: "I need $3,500"
- **Response to counter offer**: "OK I can do that"
- **Expected flow**:
  - `/carriers/verify` → eligible: true
  - `/loads/search` → Reefer load matched and pitched
  - `/negotiations/evaluate` round 1, offer $3,500 → decision: counter (counter returned)
  - `/negotiations/evaluate` round 2, carrier accepts counter → decision: accept
  - `/calls/log` → outcome: booked, sentiment: positive

---

## Script 3: Ineligible Carrier

- **Carrier MC**: INACTIVE-001
- **Expected flow**:
  - `/carriers/verify` → eligible: false, authority_status: inactive
  - Agent closes call politely, explains they cannot proceed
  - `/calls/log` → outcome: carrier_not_eligible, sentiment: neutral

---

## Script 4: No Matching Load

- **Carrier MC**: MC-555000
- **Lane**: Alaska to Hawaii, Flatbed
- **Expected flow**:
  - `/carriers/verify` → eligible: true
  - `/loads/search` → matches_found: false
  - Agent offers to check back or closes politely
  - `/calls/log` → outcome: no_matching_load, sentiment: neutral

---

## Script 5: Price Rejected After 3 Rounds

- **Carrier MC**: MC-444333
- **Lane**: Chicago to Dallas, Dry Van
- **Round 1 offer**: $3,000 (above max) → decision: counter
- **Round 2 offer**: $3,200 (above max) → decision: counter
- **Round 3 offer**: $3,500 (above max) → decision: reject
- **Expected flow**:
  - `/carriers/verify` → eligible: true
  - `/loads/search` → L-1001 matched and pitched
  - `/negotiations/evaluate` rounds 1–3 all exceed max authorized price
  - Round 3 returns reject (remaining_rounds: 0)
  - Agent closes professionally
  - `/calls/log` → outcome: price_rejected, sentiment: negative
