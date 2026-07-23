"""
Pydantic models for every request/response the API sends or accepts.
Keeping these centralized (instead of inline dicts in routers) means FastAPI's
auto-generated /docs are always accurate and typos surface as validation
errors instead of silent bugs.
"""
from enum import Enum

from pydantic import BaseModel, Field


class ReportLanguage(str, Enum):
    english = "English"
    roman_urdu = "Roman Urdu"
    urdu = "Urdu"


class UploadResponse(BaseModel):
    session_id: str
    filename: str
    file_type: str  # "spreadsheet" | "pdf"
    target_column: str | None = None
    total: float = 0.0
    row_count: int = 0
    series: list[float] = Field(default_factory=list)
    preview_text: str = ""


class ForecastResult(BaseModel):
    next_points: list[float]
    method: str
    slope: float | None = None
    note: str | None = None


class MarketData(BaseModel):
    resolved: bool
    symbol_used: str | None = None
    company_name: str | None = None
    current_price: float | str | None = None
    market_cap: float | str | None = None
    pe_ratio: float | str | None = None
    fifty_two_week_high: float | str | None = None
    fifty_two_week_low: float | str | None = None
    currency: str | None = None
    error: str | None = None


class ReportResult(BaseModel):
    compliance_report: str
    narrative_report: str
    mode: str  # "live" | "offline"
    error: str | None = None


class AnalyzeResponse(BaseModel):
    forecast: ForecastResult
    market_data: MarketData
    report: ReportResult


class ChatResponse(BaseModel):
    reply: str
    mode: str  # "live" | "offline"


class HealthResponse(BaseModel):
    status: str
    environment: str


class ErrorResponse(BaseModel):
    detail: str
