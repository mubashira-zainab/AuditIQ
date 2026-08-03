"""
AuditIQ backend entrypoint.

Run with:  uvicorn app.main:app --reload --port 8000
(from the backend/ directory, with the venv active)

Interactive API docs: http://localhost:8000/docs
"""
import os
import logging
import time
from collections import defaultdict
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Dynamic imports for file/chart generation
try:
    import pandas as pd
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from fpdf import FPDF
    _REPORT_LIBS = True
except ImportError:
    _REPORT_LIBS = False

from app.config import get_settings
from app.core.exceptions import AppError
from app.logging_config import configure_logging
from app.routers import analysis, audio, chat, health, report, upload, auth, memory
from app.db import engine
from app import models

# ─── METRICS ──────────────────────────────────────────────────────────────────
metrics: dict = {
    "total_requests": 0,
    "total_errors":   0,
    "endpoints":      defaultdict(int),
    "latencies":      [],
}

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

STATIC_DIR   = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


# ─── APP FACTORY ──────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered Financial Analysis & Decision Support System",
        version="2.0.0",
    )

    # CORS — allow all origins (restrict in production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── OBSERVABILITY MIDDLEWARE ───────────────────────────────────────────────
    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):
        start = time.time()
        metrics["total_requests"] += 1
        metrics["endpoints"][request.url.path] += 1
        try:
            response = await call_next(request)
            if response.status_code >= 400:
                metrics["total_errors"] += 1
            return response
        except Exception as exc:
            metrics["total_errors"] += 1
            raise exc
        finally:
            lat = time.time() - start
            metrics["latencies"].append(lat)
            if len(metrics["latencies"]) > 1000:
                metrics["latencies"].pop(0)

    # ── STATIC FILES ──────────────────────────────────────────────────────────
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # ── ROUTERS ───────────────────────────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(auth.router)          # NEW: /api/auth/*
    app.include_router(memory.router)        # NEW: /api/memory/*
    app.include_router(upload.router)
    app.include_router(analysis.router)
    app.include_router(audio.router)
    app.include_router(report.router)
    app.include_router(chat.router)

    # ── METRICS ENDPOINT ──────────────────────────────────────────────────────
    @app.get("/api/metrics", tags=["system"])
    async def get_metrics():
        avg = (sum(metrics["latencies"]) / len(metrics["latencies"])
               if metrics["latencies"] else 0)
        return {
            "total_requests":      metrics["total_requests"],
            "total_errors":        metrics["total_errors"],
            "error_rate":          (
                f"{metrics['total_errors'] / metrics['total_requests'] * 100:.2f}%"
                if metrics["total_requests"] > 0 else "0%"
            ),
            "avg_latency_seconds": round(avg, 4),
            "endpoints":           dict(metrics["endpoints"]),
        }

    # ── FILE GENERATOR ────────────────────────────────────────────────────────
    @app.get("/api/generate-demo-file", tags=["system"])
    async def generate_demo_file(request: Request, file_type: str = "chart"):
        if not _REPORT_LIBS:
            return JSONResponse(status_code=503, content={"error": "Report libraries not installed."})

        base_url = str(request.base_url).rstrip("/")
        host_url = (base_url if ("127.0.0.1" in base_url or "localhost" in base_url)
                    else os.getenv("BACKEND_URL", base_url))

        if file_type.lower() in ["chart", "image", "graph"]:
            plt.figure(figsize=(6, 4))
            plt.plot([1, 2, 3, 4, 5], [10, 25, 15, 30, 45], marker="o", color="#6366f1")
            plt.title("AuditIQ Performance Forecast")
            plt.xlabel("Months"); plt.ylabel("Value (PKR)")
            plt.tight_layout()
            chart_file = STATIC_DIR / "generated_chart.jpg"
            plt.savefig(chart_file); plt.close()
            return {"file_type": "chart", "url": f"{host_url}/static/generated_chart.jpg"}

        elif file_type.lower() in ["csv", "data"]:
            df = pd.DataFrame({
                "Date":       ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"],
                "Revenue":    [100000, 120000, 110000, 130000, 140000],
                "Expenses":   [40000,  50000,  45000,  55000,  60000],
                "Net Profit": [60000,  70000,  65000,  75000,  80000],
            })
            csv_file = STATIC_DIR / "financial_data.csv"
            df.to_csv(csv_file, index=False)
            return {"file_type": "csv", "url": f"{host_url}/static/financial_data.csv"}

        elif file_type.lower() in ["pdf", "report"]:
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="AuditIQ Financial Report", ln=1, align="C")
            pdf.cell(200, 10, txt="AI-generated audit analysis summary.", ln=2, align="L")
            pdf_file = STATIC_DIR / "audit_report.pdf"
            pdf.output(str(pdf_file))
            return {"file_type": "pdf", "url": f"{host_url}/static/audit_report.pdf"}

        return {"error": "Invalid file_type. Choose 'chart', 'csv', or 'pdf'."}

    # ── FAVICON ───────────────────────────────────────────────────────────────
    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        fav = PROJECT_ROOT / "favicon.ico"
        if fav.exists():
            return FileResponse(fav)
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    # ── ERROR HANDLER ─────────────────────────────────────────────────────────
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        logger.info("AppError on %s: %s", request.url.path, exc.message)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    # ── STARTUP ───────────────────────────────────────────────────────────────
    @app.on_event("startup")
    async def on_startup():
        models.Base.metadata.create_all(bind=engine)
        settings.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            "%s v2.0 started | env=%s | storage=%s",
            settings.app_name, settings.environment, settings.storage_dir,
        )

    # ── SERVE FRONTEND ────────────────────────────────────────────────────────
    if PROJECT_ROOT.exists() and (PROJECT_ROOT / "index.html").exists():
        app.mount("/", StaticFiles(directory=PROJECT_ROOT, html=True), name="web")
    else:
        logger.warning("Frontend root not found at %s", PROJECT_ROOT)

    return app


app = create_app()