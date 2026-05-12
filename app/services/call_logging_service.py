from sqlalchemy.ext.asyncio import AsyncSession
from app.models.call_log import CallLog
from app.schemas.call import CallLogRequest, CallLogResponse
import uuid


async def log_call(request: CallLogRequest, db: AsyncSession) -> CallLogResponse:
    if not request.call_id:
        request.call_id = str(uuid.uuid4())
    if request.carrier_mc_number:
        request.carrier_mc_number = str(request.carrier_mc_number)
        
    log = CallLog(
        call_id=request.call_id,
        happyrobot_run_id=request.happyrobot_run_id,
        carrier_mc_number=request.carrier_mc_number,
        carrier_name=request.carrier_name,
        selected_load_id=request.selected_load_id,
        final_offer=request.final_offer,
        outcome=request.outcome,
        sentiment=request.sentiment,
        transcript_summary=request.transcript_summary,
    )
    db.add(log)
    await db.commit()
    return CallLogResponse(success=True, call_id=request.call_id, message="Call logged successfully.")
