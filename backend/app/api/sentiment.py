"""
api/sentiment.py
POST /api/v1/analyze         — single text
POST /api/v1/analyze/batch   — list of texts
"""

from fastapi import APIRouter, HTTPException
from collections import Counter
from app.models.schemas import (
    SingleFeedbackRequest, BatchFeedbackRequest,
    SentimentResult, SentimentScores, BatchResult, BatchSummary
)
from app.core.sentiment_engine import classify, classify_batch

router = APIRouter()


def _to_result(r: dict) -> SentimentResult:
    return SentimentResult(
        text=r["text"],
        sentiment=r["sentiment"],
        confidence=r["confidence"],
        emoji=r["emoji"],
        scores=SentimentScores(
            positive=r["scores"]["positive"],
            negative=r["scores"]["negative"],
            neutral=r["scores"]["neutral"]
        )
    )


@router.post("/analyze", response_model=SentimentResult)
async def analyze_single(req: SingleFeedbackRequest):
    """Analyze sentiment of a single feedback text."""
    try:
        return _to_result(classify(req.text))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/batch", response_model=BatchResult)
async def analyze_batch(req: BatchFeedbackRequest):
    """Analyze multiple feedback texts. Returns results + aggregate summary."""
    if len(req.texts) > 500:
        raise HTTPException(status_code=400, detail="Max 500 texts per batch request.")
    try:
        raw = classify_batch(req.texts)
        total = len(raw)
        counts = Counter(r["sentiment"] for r in raw)
        avg_conf = round(sum(r["confidence"] for r in raw) / max(total, 1), 4)

        return BatchResult(
            results=[_to_result(r) for r in raw],
            summary=BatchSummary(
                total=total,
                positive={"count": counts["POSITIVE"], "percentage": round(100*counts["POSITIVE"]/total,1)},
                negative={"count": counts["NEGATIVE"], "percentage": round(100*counts["NEGATIVE"]/total,1)},
                neutral= {"count": counts["NEUTRAL"],  "percentage": round(100*counts["NEUTRAL"]/total,1)},
                average_confidence=avg_conf
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
