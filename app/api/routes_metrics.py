from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_api_key
from app.db.database import get_db
from app.services import metrics_service

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
