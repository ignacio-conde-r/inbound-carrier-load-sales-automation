from app.utils.money import compute_max_authorized_rate, round_money
from app.schemas.negotiation import NegotiationEvaluateRequest, NegotiationEvaluateResponse


def evaluate_offer(
    request: NegotiationEvaluateRequest,
    loadboard_rate: float,
    miles: int,
    equipment_type: str,
    weight: int,
    pickup_datetime_str: str = None,
) -> NegotiationEvaluateResponse:
    max_price = compute_max_authorized_rate(loadboard_rate, miles, equipment_type, weight, pickup_datetime_str)
    offer = request.carrier_offer
    round_num = request.round_number
    remaining = 3 - round_num

    if offer <= max_price:
        return NegotiationEvaluateResponse(
            decision="accept",
            agreed_price=round_money(offer),
            counter_offer=None,
            max_authorized_price=max_price,
            round_number=round_num,
            remaining_rounds=remaining,
            reason="Carrier offer is within authorized range.",
            agent_message=f"Great news! We can accept your rate of ${offer:,.2f}. Let me get you connected with our team to finalize the booking.",
        )
    elif round_num < 3:
        counter = round_money(loadboard_rate * 1.03) if round_num == 1 else round_money(max_price * 0.98)
        return NegotiationEvaluateResponse(
            decision="counter",
            agreed_price=None,
            counter_offer=counter,
            max_authorized_price=max_price,
            round_number=round_num,
            remaining_rounds=remaining,
            reason="Carrier offer exceeds authorized rate. Countering.",
            agent_message=f"I understand you're looking for ${offer:,.2f}, but the best I can do on this lane is ${counter:,.2f}. Would that work for you?",
        )
    else:
        return NegotiationEvaluateResponse(
            decision="reject",
            agreed_price=None,
            counter_offer=None,
            max_authorized_price=max_price,
            round_number=round_num,
            remaining_rounds=0,
            reason="Maximum negotiation rounds reached. Offer exceeds authorized rate.",
            agent_message=f"I appreciate your time, but unfortunately we're not able to meet your rate of ${offer:,.2f} on this load. I hope we can work together on a future opportunity.",
        )
