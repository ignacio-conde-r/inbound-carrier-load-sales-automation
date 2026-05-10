# Architecture Diagram

## System Components

```
┌─────────────────────────────────────────────────────┐
│                  HappyRobot Platform                 │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │  Web Call │  │  Voice   │  │  AI Extract/       │ │
│  │  Trigger  │→ │  Agent   │→ │  Classify/Webhook  │ │
│  └──────────┘  └────┬─────┘  └────────────────────┘ │
└───────────────────┬─┴──────────────────────────────┘
                    │ Tool calls (HTTPS + X-API-Key)
        ┌───────────▼──────────────────────┐
        │        FastAPI Backend           │
        │  /carriers/verify                │
        │  /loads/search                   │
        │  /negotiations/evaluate          │
        │  /calls/log  /metrics/*          │
        └───────────┬──────────────────────┘
                    │
        ┌───────────▼──────────────────────┐
        │     SQLite Database              │
        │  loads · call_logs ·             │
        │  negotiation_events              │
        └───────────┬──────────────────────┘
                    │
        ┌───────────▼──────────────────────┐
        │   Streamlit Dashboard            │
        │  KPIs · Sentiment · Calls ·      │
        │  Negotiation outcomes            │
        └──────────────────────────────────┘
```

## Data Flow

1. Carrier initiates web call → HappyRobot creates run
2. Agent collects MC number → calls `/carriers/verify`
3. Agent collects lane preference → calls `/loads/search`
4. Agent pitches load → carrier counters → calls `/negotiations/evaluate` (up to 3×)
5. Call ends → HappyRobot webhook calls `/calls/log`
6. Dashboard polls `/metrics/*` every 30 seconds
