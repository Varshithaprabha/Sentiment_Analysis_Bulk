# Student Feedback Sentiment Analysis System

A full-stack NLP application for automatically classifying student feedback
into Positive / Negative / Neutral, extracting themes, and generating reports.

---

## Folder Structure

```
student_feedback_system/
│
├── backend/                        ← FastAPI Python backend
│   ├── main.py                     ← App entry point, router registration, CORS
│   ├── requirements.txt            ← Python dependencies
│   └── app/
│       ├── api/                    ← HTTP route handlers (controllers)
│       │   ├── health.py           ← GET /health
│       │   ├── sentiment.py        ← POST /api/v1/analyze (single + batch)
│       │   └── reports.py          ← POST /api/v1/reports/upload, GET /export
│       ├── core/                   ← Business logic (no HTTP concerns)
│       │   ├── sentiment_engine.py ← DistilBERT + VADER dual-engine NLP
│       │   └── theme_extractor.py  ← TF-IDF keyword extraction
│       ├── models/
│       │   └── schemas.py          ← Pydantic request/response models
│       └── services/
│           └── bulk_service.py     ← CSV/Excel processing + Excel report export
│
├── frontend/
│   └── index.html                  ← Single-page dynamic dashboard (no build needed)
│
├── data/
│   └── samples/
│       └── sample_feedback.csv     ← 30-row test dataset
│
└── docs/
    └── README.md                   ← This file
```

---

## Quick Start

### Step 1 — Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload --port 8000
```

API is now live at: http://localhost:8000
Swagger docs at:   http://localhost:8000/docs

### Step 2 — Frontend

```bash
cd frontend

# No build tools needed — just open in browser:
open index.html

# Or serve with Python:
python -m http.server 3000
# Then visit http://localhost:3000
```

---

## API Reference

| Method | Endpoint                  | Description                          |
|--------|---------------------------|--------------------------------------|
| GET    | /health                   | Check API status + active NLP engine |
| POST   | /api/v1/analyze           | Classify a single feedback text      |
| POST   | /api/v1/analyze/batch     | Classify up to 500 texts at once     |
| POST   | /api/v1/reports/upload    | Upload CSV/Excel, get full report    |
| GET    | /api/v1/reports/export    | Download color-coded Excel report    |

### Single Analysis — Request
```json
POST /api/v1/analyze
{ "text": "The professor explains everything clearly and is very helpful." }
```

### Single Analysis — Response
```json
{
  "text": "The professor explains...",
  "sentiment": "POSITIVE",
  "confidence": 0.9621,
  "emoji": "😊",
  "scores": { "positive": 0.9621, "negative": 0.0210, "neutral": 0.0169 }
}
```

---

## CSV Format

Your CSV/Excel must have at least one of these column names (auto-detected):
- **Feedback column** (required): `feedback`, `comment`, `comments`, `text`, `response`
- **Category column** (optional): `category`, `department`, `course`, `faculty`, `subject`

Example:
```csv
feedback,category,faculty
"Professor is brilliant!",Computer Science,Dr. Sharma
"Lab equipment is broken.",Electronics,Dr. Mehta
```

---

## NLP Engine

**Primary (best accuracy):** HuggingFace DistilBERT
- Model: `distilbert-base-uncased-finetuned-sst-2-english`
- Downloads ~270MB on first run
- Enable: `pip install torch transformers`

**Fallback (offline, no download):** VADER
- Lexicon-based, works immediately
- Install: `pip install vaderSentiment` (included in requirements.txt)

The system auto-detects which engine is available and uses the best one.

---

## Technologies

| Technology | Role |
|---|---|
| FastAPI | REST API framework (async, auto-docs) |
| Pydantic v2 | Request/response validation |
| Uvicorn | ASGI server |
| HuggingFace Transformers | DistilBERT NLP model |
| VADER Sentiment | Offline fallback NLP engine |
| pandas | CSV/Excel I/O + data aggregation |
| openpyxl | Color-coded Excel report generation |
| scikit-learn TF-IDF | Keyword/theme extraction |
| Chart.js | Frontend charts |
| Vanilla HTML/CSS/JS | Frontend (no build tools needed) |
