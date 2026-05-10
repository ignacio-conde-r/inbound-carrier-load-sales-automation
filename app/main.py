from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_health, routes_carriers, routes_loads, routes_negotiations, routes_calls, routes_metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db.database import init_db
    await init_db()
    yield


app = FastAPI(title="HappyRobot Carrier Sales API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router, tags=["health"])
app.include_router(routes_carriers.router, prefix="/carriers", tags=["carriers"])
app.include_router(routes_loads.router, prefix="/loads", tags=["loads"])
app.include_router(routes_negotiations.router, prefix="/negotiations", tags=["negotiations"])
app.include_router(routes_calls.router, prefix="/calls", tags=["calls"])
app.include_router(routes_metrics.router, tags=["metrics"])
