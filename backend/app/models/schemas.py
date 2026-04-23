"""
models/schemas.py
Pydantic v2 schemas — define the shape of every API request and response.
FastAPI uses these for automatic validation + Swagger documentation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


# ── REQUEST SCHEMAS ───────────────────────────────────────────────────────────

class SingleFeedbackRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000,
                      example="The professor explains everything clearly and is always available.")

class BatchFeedbackRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1,
                             example=["Great course!", "Lab equipment is broken."])


# ── RESPONSE SCHEMAS ──────────────────────────────────────────────────────────

class SentimentScores(BaseModel):
    positive: float
    negative: float
    neutral: float

class SentimentResult(BaseModel):
    text: str
    sentiment: str               # "POSITIVE" | "NEGATIVE" | "NEUTRAL"
    confidence: float
    scores: SentimentScores
    emoji: str                   # Visual indicator for frontend

class BatchSummary(BaseModel):
    total: int
    positive: Dict               # {"count": int, "percentage": float}
    negative: Dict
    neutral: Dict
    average_confidence: float

class BatchResult(BaseModel):
    results: List[SentimentResult]
    summary: BatchSummary

class CategoryBreakdown(BaseModel):
    category: str
    total: int
    positive_pct: float
    negative_pct: float
    neutral_pct: float
    avg_confidence: float
    dominant_sentiment: str

class Keyword(BaseModel):
    keyword: str
    score: float
    frequency: int

class ReportSummary(BaseModel):
    total_responses: int
    sentiment_distribution: Dict
    average_confidence: float
    category_breakdown: List[CategoryBreakdown]
    themes: Dict[str, List[Keyword]]

class HealthResponse(BaseModel):
    status: str
    model: str
    version: str
    analyzer: str
