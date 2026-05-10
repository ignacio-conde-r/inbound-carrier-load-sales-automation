from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.load import Load
from app.schemas.load import LoadSearchRequest, LoadSearchResponse, LoadOption


def _pitch(load: Load) -> str:
    return (
        f"{load.origin} → {load.destination} | {load.equipment_type} | "
        f"{load.miles} miles | ${load.loadboard_rate:,.0f} | "
        f"Pickup: {load.pickup_datetime.strftime('%b %d %I:%M %p')}"
    )


def _score(load: Load, request: LoadSearchRequest) -> float:
    if not any([request.equipment_type, request.origin, request.destination]):
        return 0.5
    score = 0.0
    if request.equipment_type and load.equipment_type == request.equipment_type:
        score += 0.4
    if request.origin and request.origin.lower() in load.origin.lower():
        score += 0.3
    if request.destination and request.destination.lower() in load.destination.lower():
        score += 0.3
    return score


def _to_option(load: Load, score: float) -> LoadOption:
    return LoadOption(
        load_id=load.load_id,
        origin=load.origin,
        destination=load.destination,
        pickup_datetime=load.pickup_datetime,
        delivery_datetime=load.delivery_datetime,
        equipment_type=load.equipment_type,
        loadboard_rate=load.loadboard_rate,
        weight=load.weight,
        commodity_type=load.commodity_type,
        miles=load.miles,
        notes=load.notes or None,
        match_score=score,
        pitch_summary=_pitch(load),
    )


async def search_loads(request: LoadSearchRequest, db: AsyncSession) -> LoadSearchResponse:
    stmt = select(Load).where(Load.status == "available")

    if request.equipment_type:
        stmt = stmt.where(Load.equipment_type == request.equipment_type)
    if request.origin:
        stmt = stmt.where(Load.origin.ilike(f"%{request.origin}%"))
    if request.destination:
        stmt = stmt.where(Load.destination.ilike(f"%{request.destination}%"))
    if request.pickup_after:
        stmt = stmt.where(Load.pickup_datetime >= request.pickup_after)
    if request.max_weight:
        stmt = stmt.where(Load.weight <= request.max_weight)

    result = await db.execute(stmt)
    loads = result.scalars().all()

    scored = sorted(
        [(_score(load, request), load) for load in loads],
        key=lambda x: x[0],
        reverse=True,
    )

    if not scored:
        return LoadSearchResponse(matches_found=False, total_matches=0)

    recommended = _to_option(scored[0][1], scored[0][0])
    alternatives = [_to_option(load, score) for score, load in scored[1:3]]

    return LoadSearchResponse(
        matches_found=True,
        total_matches=len(scored),
        recommended_load=recommended,
        alternatives=alternatives,
    )
