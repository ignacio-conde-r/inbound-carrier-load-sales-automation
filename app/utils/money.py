def round_money(amount: float) -> float:
    return round(amount, 2)


def compute_max_authorized_rate(
    loadboard_rate: float,
    miles: int,
    equipment_type: str,
    weight: int,
    pickup_datetime_str: str = None,
) -> float:
    from datetime import datetime, timezone

    rate = loadboard_rate
    if miles <= 300:
        pct = 0.05
    elif miles <= 900:
        pct = 0.08
    else:
        pct = 0.10

    if equipment_type == "Reefer":
        pct += 0.02

    if weight > 42000:
        pct = min(pct, 0.05)

    if pickup_datetime_str:
        try:
            pickup = datetime.fromisoformat(pickup_datetime_str)
            now = datetime.now(timezone.utc)
            if pickup.tzinfo is None:
                pickup = pickup.replace(tzinfo=timezone.utc)
            hours_until = (pickup - now).total_seconds() / 3600
            if hours_until <= 24:
                pct += 0.03
        except Exception:
            pass

    max_rate = loadboard_rate * (1 + pct)
    return round_money(max_rate)
