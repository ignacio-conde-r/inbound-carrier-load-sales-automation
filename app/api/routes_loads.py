from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_api_key
from app.db.database import get_db
from app.schemas.load import LoadSearchRequest, LoadSearchResponse
from app.services import load_matching_service

router = APIRouter()


@router.post(
    "/search",
    response_model=LoadSearchResponse,
    dependencies=[Depends(get_api_key)],
    name="Search Loads",
)
async def search_loads(request: LoadSearchRequest, db: AsyncSession = Depends(get_db)):
    return await load_matching_service.search_loads(request, db)
