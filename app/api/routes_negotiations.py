from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_api_key
from app.db.database import get_db
from app.schemas.negotiation import NegotiationEvaluateRequest, NegotiationEvaluateResponse
from app.services import negotiation_service

router = APIRouter()


@router.post(
    "/evaluate",
    response_model=NegotiationEvaluateResponse,
    dependencies=[Depends(get_api_key)],
    name="Evaluate Negotiation Offer",
)
async def evaluate_negotiation(request: NegotiationEvaluateRequest, db: AsyncSession = Depends(get_db)):
    return await negotiation_service.process_negotiation(request, db)
