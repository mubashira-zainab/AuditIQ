"""
AuditIQ backend entrypoint.

Run with:  uvicorn app.main:app --reload --port 8000
(from the project root, with the venv active)

Interactive API docs available at /docs once running.
"""
import os
import logging
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Dynamic library imports for automatic file & chart generation
try:
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from fpdf import FPDF
except ImportError:
    pass

from app.config import get_settings
from app.core.exceptions import AppError
from app.logging_config import configure_logging
from app.routers import analysis, audio, chat, health, report, upload

# Set default Environment variables for Groq Key & Render Backend URL
os.environ.setdefault("GROQ_API_KEY", "")
os.environ.setdefault("BACKEND_URL", "http://127.0.0.1:8000")

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

# Static storage inside app
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Main Project Root Directory (Where your original index.html, style.css, app.js live)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static files endpoint for serving backend uploads/downloads
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # Include modular routes
    app.include_router(health.router)
    app.include_router(upload.router)
    app.include_router(analysis.router)
    app.include_router(audio.router)
    app.include_router(report.router)
    app.include_router(chat.router)

    # Explicit backend image & file upload validation patch
    @app.post("/api/upload-fix")
    async def upload_file_fix(file: UploadFile = File(...)):
        filename = file.filename.lower()
        allowed_extensions = (".csv", ".xlsx", ".pdf", ".png", ".jpg", ".jpeg")
        if not filename.endswith(allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        return {"filename": file.filename, "status": "success", "message": "File format allowed successfully!"}

    # Helper Endpoint: Direct File / Chart / CSV / PDF Generator
    @app.get("/api/generate-demo-file")
    async def generate_demo_file(file_type: str = "chart"):
        host_url = os.getenv("BACKEND_URL", "https://auditiq-f8t8.onrender.com")
        
        # 1. Image Chart Generator (.jpg)
        if file_type.lower() in ["chart", "image", "graph"]:
            plt.figure(figsize=(6, 4))
            plt.plot([1, 2, 3, 4, 5], [10, 25, 15, 30, 45], marker='o', color='#00a896', label='Audit Revenue')
            plt.title('AuditIQ Performance Forecast')
            plt.xlabel('Months')
            plt.ylabel('Value (PKR)')
            plt.legend()
            chart_file = STATIC_DIR / "generated_chart.jpg"
            plt.savefig(chart_file)
            plt.close()
            return {"file_type": "chart", "url": f"{host_url}/static/generated_chart.jpg"}

        # 2. CSV Data File Generator (.csv)
        elif file_type.lower() in ["csv", "data"]:
            df = pd.DataFrame({
                "Date": ["2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01", "2026-05-01"],
                "Revenue": [100000, 120000, 110000, 130000, 140000],
                "Expenses": [40000, 50000, 45000, 55000, 60000],
                "Net Profit": [60000, 70000, 65000, 75000, 80000]
            })
            csv_file = STATIC_DIR / "financial_data.csv"
            df.to_csv(csv_file, index=False)
            return {"file_type": "csv", "url": f"{host_url}/static/financial_data.csv"}

        # 3. PDF Audit Report Generator (.pdf)
        elif file_type.lower() in ["pdf", "report"]:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="AuditIQ Comprehensive Financial Report", ln=1, align='C')
            pdf.cell(200, 10, txt="Automated AI Audit Analysis & Verification Summary.", ln=2, align='L')
            pdf_file = STATIC_DIR / "audit_report.pdf"
            pdf.output(pdf_file)
            return {"file_type": "pdf", "url": f"{host_url}/static/audit_report.pdf"}

        return {"error": "Invalid file_type requested. Choose 'chart', 'csv', or 'pdf'."}

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> FileResponse:
        fav = PROJECT_ROOT / "favicon.ico"
        if fav.exists():
            return FileResponse(fav)
        return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.info("Handled error on %s: %s", request.url.path, exc.message)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.on_event("startup")
    async def on_startup() -> None:
        settings.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info("%s started (env=%s, storage=%s)", settings.app_name, settings.environment, settings.storage_dir)

    # Mount exact root directory where your original style.css, app.js and index.html are located
    if PROJECT_ROOT.exists() and (PROJECT_ROOT / "index.html").exists():
        app.mount("/", StaticFiles(directory=PROJECT_ROOT, html=True), name="web")
    else:
        logger.warning("Frontend root folder not found at %s", PROJECT_ROOT)

    return app
app = create_app()