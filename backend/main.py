"""
main.py — FastAPI application entry point
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import sentiment, reports, health

app = FastAPI(
    title="Student Feedback Sentiment API",
    description="NLP-powered sentiment analysis for university feedback",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router,    tags=["Health"])
app.include_router(sentiment.router, prefix="/api/v1", tags=["Sentiment Analysis"])
app.include_router(reports.router,   prefix="/api/v1", tags=["Reports"])

@app.get("/api/status/{status_id}", tags=["Diagnostic"])
async def diagnostic_status(status_id: int):
    """Temporary route to handle unknown monitoring requests."""
    return {"status": "operational", "id": status_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
