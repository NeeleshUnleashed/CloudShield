from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager

from app.config import settings
from app.db.seed_data import seed_database
from app.api.routes_disaster import router as disaster_router
from app.api.routes_inventory import router as inventory_router
from app.api.routes_alerts import router as alerts_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure DB is seeded on startup
    seed_database(force_reset=False)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Disaster Response, Prediction & Supply Allocation Engine",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(disaster_router)
app.include_router(inventory_router)
app.include_router(alerts_router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "aws_mode": settings.AWS_MODE,
        "aws_region": settings.AWS_REGION,
        "cost_policy": "Zero Unexpected Charges Enforced (Mock Mode)"
    }

# Mount static frontend directory
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
