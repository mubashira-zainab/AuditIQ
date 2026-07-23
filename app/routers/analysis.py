"""Runs the forecast + market lookup + AI report pipeline for a previously uploaded session."""
import logging

from fastapi import APIRouter, Depends, Form

from app.config import Settings, get_settings
from app.dependencies import get_session_store
from app.schemas import AnalyzeResponse, ForecastResult, MarketData, ReportLanguage, ReportResult
from app.services.ai_pipeline import run_report_pipeline
from app.services.forecaster import forecast_series
from app.services.market_watcher import get_live_market_data
from app.services.session_store import SessionStore

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analysis"])


@router.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(
    session_id: str = Form(...),
    ticker: str = Form(""),
    language: ReportLanguage = Form(ReportLanguage.english),
    api_key: str = Form(""),
    horizon: int | None = Form(None),
    settings: Settings = Depends(get_settings),
    store: SessionStore = Depends(get_session_store),
) -> AnalyzeResponse:
    session = store.get(session_id)
    upload = session.upload

    effective_horizon = horizon or settings.default_forecast_horizon
    effective_horizon = min(effective_horizon, settings.max_forecast_horizon)

    forecast = forecast_series(upload.get("series", []), horizon=effective_horizon)
    market_data = get_live_market_data(ticker) if ticker.strip() else {"resolved": False}

    context = {
        "ticker": ticker,
        "market_data": market_data,
        "total": upload.get("total", 0.0),
        "row_count": upload.get("row_count", 0),
        "target_column": upload.get("target_column"),
        "forecast_points": forecast.get("next_points", []),
        "source_preview": upload.get("preview_text", ""),
    }

    report = run_report_pipeline(context, language=language.value, api_key=api_key.strip() or None, settings=settings)

    store.update(session_id, analysis={"forecast": forecast, "market_data": market_data, "report": report}, language=language.value)
    logger.info("Analysis complete: session=%s mode=%s ticker=%s", session_id, report.get("mode"), ticker or "none")

    return AnalyzeResponse(
        forecast=ForecastResult(**forecast),
        market_data=MarketData(**market_data),
        report=ReportResult(**report),
    )
