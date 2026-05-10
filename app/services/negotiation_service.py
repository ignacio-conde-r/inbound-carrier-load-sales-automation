from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.load import Load
from app.models.negotiation import NegotiationEvent
from app.schemas.negotiation import NegotiationEvaluateRequest, NegotiationEvaluateResponse
from app.services.pricing_policy import evaluate_offer


async def process_negotiation(request: NegotiationEvaluateRequest, db: AsyncSession) -> NegotiationEvaluateResponse:
    result = await db.execute(select(Load).where(Load.load_id == request.load_id))
    load = result.scalars().first()

    if not load:
        return NegotiationEvaluateResponse(
            decision="reject",
            agreed_price=None,
            counter_offer=None,
            max_authorized_price=0.0,
            round_number=request.round_number,
            remaining_rounds=0,
            reason="Load not found.",
            agent_message="I'm sorry, I wasn't able to locate that load in our system.",
        )

    pickup_str = load.pickup_datetime.isoformat() if load.pickup_datetime else None
    response = evaluate_offer(request, load.loadboard_rate, load.miles, load.equipment_type, load.weight, pickup_str)

    event = NegotiationEvent(
        call_id=request.call_id,
        load_id=request.load_id,
        carrier_mc_number=request.carrier_mc_number,
        round_number=request.round_number,
        carrier_offer=request.carrier_offer,
        counter_offer=response.counter_offer,
        decision=response.decision,
        max_authorized_price=response.max_authorized_price,
    )
    db.add(event)
    await db.commit()
    return response
