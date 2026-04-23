"""
core/sentiment_engine.py
========================
Dual-engine sentiment analysis:
  PRIMARY   → HuggingFace DistilBERT (downloads ~270MB on first run, best accuracy)
  FALLBACK  → VADER (offline, no download needed, good for social/academic text)

The engine auto-detects which is available and uses the best option.
"""

import re
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# ── ENGINE DETECTION ──────────────────────────────────────────────────────────

def _try_load_transformers():
    """Attempt to load HuggingFace pipeline. Returns pipeline or None."""
    try:
        from transformers import pipeline
        nlp = pipeline(
            "text-classification",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            top_k=None,
            truncation=True,
            max_length=512
        )
        logger.info("✅ DistilBERT loaded successfully.")
        return nlp, "distilbert"
    except Exception as e:
        logger.warning(f"DistilBERT unavailable ({e}). Falling back to VADER.")
        return None, None


def _load_vader():
    """Load VADER analyzer."""
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    logger.info("✅ VADER analyzer loaded.")
    return SentimentIntensityAnalyzer(), "vader"


# Lazy singletons — loaded once, reused for every request
_nlp_pipeline = None
_vader_analyzer = None
_active_engine = None


def get_engine():
    global _nlp_pipeline, _vader_analyzer, _active_engine
    if _active_engine:
        return _active_engine

    pipeline, engine_name = _try_load_transformers()
    if pipeline:
        _nlp_pipeline = pipeline
        _active_engine = engine_name
        return engine_name

    analyzer, engine_name = _load_vader()
    _vader_analyzer = analyzer
    _active_engine = engine_name
    return engine_name


# ── PREPROCESSING ─────────────────────────────────────────────────────────────

def preprocess(text: str) -> str:
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'http\S+|www\S+', '', text)  # Remove URLs
    return text


# ── CLASSIFICATION ────────────────────────────────────────────────────────────

NEUTRAL_THRESHOLD = 0.65   # Confidence below this → NEUTRAL
EMOJI_MAP = {"POSITIVE": "😊", "NEGATIVE": "😞", "NEUTRAL": "😐"}


def _classify_distilbert(text: str) -> dict:
    raw = _nlp_pipeline(text)[0]
    score_map = {item["label"]: item["score"] for item in raw}
    pos = score_map.get("POSITIVE", 0.0)
    neg = score_map.get("NEGATIVE", 0.0)

    if pos >= NEUTRAL_THRESHOLD:
        sentiment, confidence = "POSITIVE", pos
    elif neg >= NEUTRAL_THRESHOLD:
        sentiment, confidence = "NEGATIVE", neg
    else:
        sentiment = "NEUTRAL"
        confidence = 1.0 - abs(pos - neg)

    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 4),
        "scores": {
            "positive": round(pos, 4),
            "negative": round(neg, 4),
            "neutral":  round(max(0.0, 1.0 - pos - neg), 4)
        }
    }


def _classify_vader(text: str) -> dict:
    scores = _vader_analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        sentiment = "POSITIVE"
        confidence = round((compound + 1) / 2, 4)
    elif compound <= -0.05:
        sentiment = "NEGATIVE"
        confidence = round((1 - compound) / 2, 4)
    else:
        sentiment = "NEUTRAL"
        confidence = round(1 - abs(compound), 4)

    pos = round(scores["pos"], 4)
    neg = round(scores["neg"], 4)
    neu = round(scores["neu"], 4)

    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "scores": {"positive": pos, "negative": neg, "neutral": neu}
    }


def classify(text: str) -> dict:
    """
    Classify a single feedback string.
    Returns: { text, sentiment, confidence, scores, emoji }
    """
    if not text or not text.strip():
        return {
            "text": text, "sentiment": "NEUTRAL", "confidence": 1.0,
            "scores": {"positive": 0.0, "negative": 0.0, "neutral": 1.0},
            "emoji": "😐"
        }

    cleaned = preprocess(text)
    engine = get_engine()

    if engine == "distilbert":
        result = _classify_distilbert(cleaned)
    else:
        result = _classify_vader(cleaned)

    result["text"] = text
    result["emoji"] = EMOJI_MAP[result["sentiment"]]
    return result


def classify_batch(texts: list) -> list:
    """Classify a list of texts. Returns list of classify() results."""
    return [classify(t) for t in texts]


def get_engine_info() -> dict:
    engine = get_engine()
    return {
        "analyzer": engine,
        "model": "distilbert-base-uncased-finetuned-sst-2-english" if engine == "distilbert" else "VADER Lexicon v3.3",
        "neutral_threshold": NEUTRAL_THRESHOLD
    }
