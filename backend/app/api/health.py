"""api/health.py — Health check endpoint"""

from fastapi import APIRouter
from app.core.sentiment_engine import get_engine_info
from app.models.schemas import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health():
    info = get_engine_info()
    return HealthResponse(
        status="healthy",
        model=info["model"],
        version="1.0.0",
        analyzer=info["analyzer"]
    )
