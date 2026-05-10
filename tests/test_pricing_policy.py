import pytest
from app.schemas.negotiation import NegotiationEvaluateRequest
from app.services.pricing_policy import evaluate_offer


def make_request(call_id, load_id, mc, round_num, offer):
    return NegotiationEvaluateRequest(
        call_id=call_id, load_id=load_id, carrier_mc_number=mc, round_number=round_num, carrier_offer=offer
    )


def test_accept_within_range():
    req = make_request("c1", "L-1001", "MC-123", 1, 2500.0)
    r = evaluate_offer(req, 2450.0, 925, "Dry Van", 38000)
    assert r.decision == "accept"
    assert r.agreed_price == 2500.0


def test_counter_round_1():
    req = make_request("c1", "L-1001", "MC-123", 1, 3000.0)
    r = evaluate_offer(req, 2450.0, 925, "Dry Van", 38000)
    assert r.decision == "counter"
    assert r.counter_offer is not None


def test_reject_round_3():
    req = make_request("c1", "L-1001", "MC-123", 3, 3000.0)
    r = evaluate_offer(req, 2450.0, 925, "Dry Van", 38000)
    assert r.decision == "reject"


def test_max_rate_long_haul():
    from app.utils.money import compute_max_authorized_rate
    max_r = compute_max_authorized_rate(2450.0, 925, "Dry Van", 38000)
    assert max_r == round(2450.0 * 1.10, 2)


def test_max_rate_reefer_bonus():
    from app.utils.money import compute_max_authorized_rate
    max_r = compute_max_authorized_rate(2450.0, 925, "Reefer", 38000)
    assert max_r == round(2450.0 * 1.12, 2)
