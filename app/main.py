"""
AuditIQ backend entrypoint.

Run with:  uvicorn app.main:app --reload --port 8000
(from the project root, with the venv active)

Interactive API docs available at /docs once running.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.exceptions import AppError
from app.logging_config import configure_logging
from app.routers import analysis, audio, chat, health, report, upload

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mubashira-zainab.github.io",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(upload.router)
    app.include_router(analysis.router)
    app.include_router(audio.router)
    app.include_router(report.router)
    app.include_router(chat.router)

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.info("Handled error on %s: %s", request.url.path, exc.message)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.on_event("startup")
    async def on_startup() -> None:
        settings.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info("%s started (env=%s, storage=%s)", settings.app_name, settings.environment, settings.storage_dir)

    return app


app = create_app()

@app.get("/")
async def root():
    return {
        "message": "AuditIQ API is running successfully!"
    }
