# Inbound Carrier Sales Automation — Solution Overview

## Prepared for: Acme Logistics
## Submitted by: Ignacio Conros, Forward Deployed Engineer

---

## Executive Summary

Acme Logistics currently handles inbound carrier calls manually — a dispatcher answers, verifies the carrier's authority, searches for an available load that matches the carrier's lane and equipment, negotiates a rate, and records the outcome. This solution automates that entire workflow end to end using HappyRobot's AI voice platform backed by a deterministic policy engine that enforces pricing rules, so no call is ever lost to hold times and no deal is ever made outside authorized margins.

The result is a system that vets carriers against live FMCSA data, matches them to the best available load using a scored search, negotiates pricing within pre-approved margins for up to three rounds, logs every call outcome and sentiment score, and surfaces all of that in a live operations dashboard — all without a human dispatcher on the first call. Dispatchers step in only when a deal closes or an exception requires escalation.

---

## How It Works

**Step 1 — Carrier Calls In.** A carrier dials Acme's inbound number. HappyRobot's voice platform answers instantly, greets the carrier professionally, and begins collecting the information needed to route the call: their MC number, the lane they want to run, their equipment type, and their availability window.

**Step 2 — FMCSA Eligibility Verification.** The moment the carrier provides their MC number, the system queries the FMCSA database in real time. It checks operating authority status and safety rating. If the carrier is active and in good standing, the conversation continues. If not, the agent explains the situation politely and closes the call — no load details are ever shared with an ineligible carrier.

**Step 3 — Load Matching.** Once the carrier is verified, the agent searches Acme's available load inventory using the carrier's stated origin, destination, and equipment type. Each candidate load is scored for relevance and the best match is pitched to the carrier with a concise summary: lane, miles, commodity, and rate. Up to two alternatives are available if the carrier isn't interested in the top match.

**Step 4 — Price Negotiation.** If the carrier wants to negotiate, the system runs their counteroffer through a deterministic pricing policy engine. The engine knows the maximum authorized rate for each load — calculated from the listed rate, distance, equipment type, and urgency — and responds with an accept, a counter, or a final rejection. This happens up to three rounds. The AI agent reads out the decision naturally; it never sets the price itself.

**Step 5 — Outcome Logging and Dashboard Update.** When the call ends, HappyRobot sends a structured webhook to the backend with the final outcome (booked, price rejected, no matching load, carrier not eligible, etc.) and a sentiment classification. That data is written to the database immediately and reflected in the operations dashboard within 30 seconds, giving Acme's team a live view of booking rate, average agreed price, and carrier sentiment across all calls.

---

## What We Built

- **Voice Agent**: HappyRobot workflow handling the real-time conversation, tool orchestration, data extraction, and outcome classification.
- **Policy Engine**: Deterministic FastAPI backend enforcing pricing rules by lane, distance, equipment type, and urgency. The AI never sets prices — the engine does.
- **Load Database**: 30 available loads across major US freight lanes seeded into SQLite, searchable by origin, destination, equipment type, and pickup window.
- **Operations Dashboard**: Real-time Streamlit dashboard showing booking rate, sentiment analysis, negotiation outcomes, and call history — built from our own data, not platform analytics.
- **Infrastructure**: Fully containerized with Docker Compose. Deployable to any cloud provider in minutes.

---

## Security

- HTTPS on all deployed endpoints
- X-API-Key authentication on all non-health endpoints
- API keys stored in environment variables, never in code
- FMCSA live mode available; mock mode for demo reliability

---

## Business Value

- **Dispatcher time saved**: Every first-touch carrier call — verification, load matching, and up to three negotiation rounds — is handled automatically, freeing dispatchers from calls that would otherwise take 10–20 minutes each.
- **Consistent pricing policy enforcement**: Every rate decision is made by the same deterministic engine with the same rules, eliminating under-pricing from rushed negotiations and over-pricing that loses carriers.
- **Full auditability**: Every negotiation round, carrier offer, counter, and final decision is persisted with a timestamp. Acme has a complete record of every call outcome for compliance, coaching, and rate analysis.

---

## Deployment

Currently deployed at: [DEPLOYMENT_URL — to be filled]  
Dashboard: [DASHBOARD_URL — to be filled]  
Repository: [GITHUB_URL — to be filled]
