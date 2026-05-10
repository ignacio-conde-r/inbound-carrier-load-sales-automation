from fastapi import APIRouter, Depends
from app.dependencies import get_api_key
from app.schemas.carrier import CarrierVerifyRequest, CarrierVerifyResponse
from app.services import fmcsa_client

router = APIRouter()


@router.post(
    "/verify",
    response_model=CarrierVerifyResponse,
    dependencies=[Depends(get_api_key)],
    name="Verify Carrier",
)
async def verify_carrier(request: CarrierVerifyRequest):
    return await fmcsa_client.verify_carrier(request.mc_number)
