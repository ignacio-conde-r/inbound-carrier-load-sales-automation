from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.call_log import CallLog
from app.models.negotiation import NegotiationEvent
from app.schemas.metrics import MetricsSummary


async def get_summary(db: AsyncSession) -> MetricsSummary:
    result = await db.execute(select(CallLog))
    logs = result.scalars().all()
    total = len(logs)
    booked = sum(1 for l in logs if l.outcome == "booked")
    ineligible = sum(1 for l in logs if l.outcome == "carrier_not_eligible")
    no_match = sum(1 for l in logs if l.outcome == "no_matching_load")
    price_rejected = sum(1 for l in logs if l.outcome == "price_rejected")
    positive = sum(1 for l in logs if l.sentiment == "positive")
    negative = sum(1 for l in logs if l.sentiment == "negative")
    booked_logs = [l for l in logs if l.outcome == "booked" and l.final_offer]
    avg_price = round(sum(l.final_offer for l in booked_logs) / len(booked_logs), 2) if booked_logs else None
    booking_rate = round(booked / total, 4) if total > 0 else 0.0

    neg_result = await db.execute(select(NegotiationEvent))
    events = neg_result.scalars().all()
    call_rounds = {}
    for e in events:
        call_rounds.setdefault(e.call_id, 0)
        call_rounds[e.call_id] = max(call_rounds[e.call_id], e.round_number)
    avg_rounds = round(sum(call_rounds.values()) / len(call_rounds), 2) if call_rounds else None

    return MetricsSummary(
        total_calls=total,
        booked=booked,
        booking_rate=booking_rate,
        ineligible=ineligible,
        no_match=no_match,
        price_rejected=price_rejected,
        avg_agreed_price=avg_price,
        avg_negotiation_rounds=avg_rounds,
        positive_sentiment=positive,
        negative_sentiment=negative,
    )


async def get_recent_calls(db: AsyncSession, limit: int = 20):
    result = await db.execute(
        select(CallLog).order_by(CallLog.created_at.desc()).limit(limit)
    )
    logs = result.scalars().all()
    return [
        {
            "call_id": l.call_id,
            "carrier_mc": l.carrier_mc_number,
            "carrier_name": l.carrier_name,
            "load_id": l.selected_load_id,
            "final_offer": l.final_offer,
            "outcome": l.outcome,
            "sentiment": l.sentiment,
            "summary": l.transcript_summary,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]


async def get_negotiation_stats(db: AsyncSession):
    result = await db.execute(select(NegotiationEvent))
    events = result.scalars().all()
    return [
        {
            "call_id": e.call_id,
            "load_id": e.load_id,
            "round": e.round_number,
            "carrier_offer": e.carrier_offer,
            "counter_offer": e.counter_offer,
            "decision": e.decision,
            "max_authorized": e.max_authorized_price,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]
