from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_api_key
from app.db.database import get_db
from app.services import metrics_service
from sqlalchemy import delete
from app.models.call_log import CallLog
from app.models.negotiation import NegotiationEvent

router = APIRouter()


@router.get("/metrics/summary")
async def summary(db: AsyncSession = Depends(get_db), api_key: str = Depends(get_api_key)):
    return await metrics_service.get_summary(db)


@router.get("/metrics/calls")
async def recent_calls(db: AsyncSession = Depends(get_db), api_key: str = Depends(get_api_key)):
    return await metrics_service.get_recent_calls(db)


@router.get("/metrics/negotiations")
async def negotiation_stats(db: AsyncSession = Depends(get_db), api_key: str = Depends(get_api_key)):
    return await metrics_service.get_negotiation_stats(db)

@router.delete("/admin/reset")
async def reset_data(db: AsyncSession = Depends(get_db), api_key: str = Depends(get_api_key)):
    await db.execute(delete(NegotiationEvent))
    await db.execute(delete(CallLog))
    await db.commit()
    return {"success": True, "message": "All call logs and negotiation events deleted"}