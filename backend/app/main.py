"""
FastAPI integration layer for Amazon PPC Search Term Analyzer.

Endpoints:
  POST /api/analyze
  GET  /api/download/report/{session_id}
  GET  /api/download/bulk/{session_id}
"""

from __future__ import annotations

import io
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from .analyzer import SearchTermAnalyzer
from .bulk_generator import generate_bulk_csv
from .exporter import generate_report


app = FastAPI(
    title="Amazon PPC Search Term Analyzer API",
    version="1.0.0",
)


def _parse_cors_origins() -> list[str]:
    raw = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory session store (file-in, file-out utility; no persistent database).
SESSIONS: Dict[str, Dict[str, Any]] = {}

DEFAULT_THRESHOLDS = {
    "click_threshold": 10,
    "acos_threshold": 0.30,
    "cvr_threshold": 0.10,
    "low_click_threshold": 10,
    "order_threshold": 2,
}


@app.get("/api/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze_report(
    file: UploadFile = File(...),
    thresholds: str = Form("{}"),
) -> JSONResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing uploaded file name.")

    filename_lower = file.filename.lower()
    if not (filename_lower.endswith(".csv") or filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Only .csv, .xlsx, and .xls files are supported.")

    try:
        user_thresholds = json.loads(thresholds) if thresholds else {}
        merged_thresholds = {**DEFAULT_THRESHOLDS, **user_thresholds}
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid thresholds JSON.") from exc

    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        analyzer = SearchTermAnalyzer()
        file_type = "csv" if filename_lower.endswith(".csv") else "excel"
        analyzer.load_data(content, file_type=file_type)
        results = analyzer.analyze(merged_thresholds)

        report_bytes = generate_report(results)
        wasted_df = results["Wasted Adspend"]
        bulk_bytes = generate_bulk_csv(wasted_df)

        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "report_bytes": report_bytes,
            "bulk_bytes": bulk_bytes,
        }

        categories = []
        for name, df in results.items():
            categories.append(
                {
                    "name": name,
                    "count": int(len(df)),
                    "totalClicks": int(df["Clicks"].sum()) if "Clicks" in df.columns else 0,
                    "totalSpend": float(df["Spend"].sum()) if "Spend" in df.columns else 0.0,
                    "totalOrders": int(df["Orders"].sum()) if "Orders" in df.columns else 0,
                    "avgAcos": float(df["ACOS"].mean()) if "ACOS" in df.columns and len(df) else 0.0,
                }
            )

        return JSONResponse(
            {
                "session_id": session_id,
                "categories": categories,
            }
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(exc)}") from exc


@app.get("/api/download/report/{session_id}")
def download_report(session_id: str) -> StreamingResponse:
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    report_bytes: bytes = session["report_bytes"]
    filename = f"Analyzer_Report_{session_id[:8]}.xlsx"
    return StreamingResponse(
        io.BytesIO(report_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/download/bulk/{session_id}")
def download_bulk(session_id: str) -> StreamingResponse:
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    bulk_bytes: bytes = session["bulk_bytes"]
    filename = f"Bulk_Negation_{session_id[:8]}.csv"
    return StreamingResponse(
        io.BytesIO(bulk_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
