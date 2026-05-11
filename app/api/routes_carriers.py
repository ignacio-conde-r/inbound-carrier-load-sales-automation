from fastapi import APIRouter, Depends #API router: defines a group of related endpoints
from app.dependencies import get_api_key # Imports the function that validates the X-API-Key header. It will be used to protect this endpoint from unauthenticated requests.
from app.schemas.carrier import CarrierVerifyRequest, CarrierVerifyResponse # imports Pydantic models
from app.services import fmcsa_client

router = APIRouter()


@router.post(
    "/verify",
    response_model=CarrierVerifyResponse, # tells FastAPI to validate and serialize the return value against that schema, documents it correctly in Swagger UI
    dependencies=[Depends(get_api_key)], # ensures that the endpoint is protected by the API key validation
    name="Verify Carrier", # display name shown in /docs 
)
async def verify_carrier(request: CarrierVerifyRequest): # FastAPI reads the type annotation CarrierVerifyRequest on the request parameter and automatically parses and validates the request body JSON against that schema before calling this function.
    return await fmcsa_client.verify_carrier(request.mc_number) # calls the service and returns its result. No business logic lives here.
