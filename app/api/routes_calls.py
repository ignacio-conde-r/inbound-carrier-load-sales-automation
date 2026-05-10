from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_api_key
from app.db.database import get_db
from app.schemas.call import CallLogRequest, CallLogResponse
from app.services import call_logging_service

router = APIRouter()


@router.post(
    "/log",
    response_model=CallLogResponse,
    dependencies=[Depends(get_api_key)],
    name="Log Call",
)
async def log_call(request: CallLogRequest, db: AsyncSession = Depends(get_db)):
    return await call_logging_service.log_call(request, db)
