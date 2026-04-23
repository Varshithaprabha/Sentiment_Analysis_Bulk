"""
api/reports.py
POST /api/v1/reports/upload  — Upload CSV/Excel, get full sentiment report
GET  /api/v1/reports/export  — Download the color-coded Excel report
"""

import tempfile, shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from app.services.bulk_service import process_file

router = APIRouter()

# In-memory store for the last processed files
_last_excel: bytes = None
_last_csv: bytes = None


@router.post("/reports/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    global _last_excel, _last_csv

    allowed = {".csv", ".xlsx", ".xls"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, f"File type '{suffix}' not supported. Use: {allowed}")

    tmp_dir = tempfile.mkdtemp()
    tmp_path = Path(tmp_dir) / f"upload{suffix}"

    try:
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        result = process_file(str(tmp_path))
        _last_excel = result["excel_bytes"]
        _last_csv = result["csv_bytes"]
        return {"status": "success", "summary": result["summary"]}

    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@router.get("/reports/export")
async def export_excel():
    """Download the color-coded Excel report (with summary sheets)."""
    if not _last_excel:
        raise HTTPException(404, "No report available. Upload a file first.")
    return Response(
        content=_last_excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=sentiment_report.xlsx"}
    )


@router.get("/reports/export/csv")
async def export_csv():
    """Download the raw sentiment data as a CSV."""
    if not _last_csv:
        raise HTTPException(404, "No report available. Upload a file first.")
    return Response(
        content=_last_csv,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sentiment_data.csv"}
    )
