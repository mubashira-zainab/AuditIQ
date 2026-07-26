"""
Pydantic models for every request/response the API sends or accepts.
Keeping these centralized (instead of inline dicts in routers) means FastAPI's
auto-generated /docs are always accurate and typos surface as validation
errors instead of silent bugs.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ReportLanguage(str, Enum):
    english    = "English"
    roman_urdu = "Roman Urdu"
    urdu       = "Urdu"


class UploadResponse(BaseModel):
    session_id:    str
    filename:      str
    file_type:     str  # "spreadsheet" | "pdf" | "image"
    target_column: Optional[str] = None
    total:         float = 0.0
    row_count:     int   = 0
    series:        list[float] = Field(default_factory=list)
    preview_text:  str = ""


class ForecastResult(BaseModel):
    next_points: list[float]
    method:      str
    slope:       Optional[float] = None
    note:        Optional[str]   = None


class MarketData(BaseModel):
    resolved:           bool
    symbol_used:        Optional[str]         = None
    company_name:       Optional[str]         = None
    current_price:      Optional[float | str] = None
    market_cap:         Optional[float | str] = None
    pe_ratio:           Optional[float | str] = None
    fifty_two_week_high: Optional[float | str] = None
    fifty_two_week_low:  Optional[float | str] = None
    currency:           Optional[str]         = None
    error:              Optional[str]         = None


class ReportResult(BaseModel):
    compliance_report: str
    narrative_report:  str
    mode:              str  # "live" | "offline"
    error:             Optional[str] = None


class AnalyzeResponse(BaseModel):
    forecast:    ForecastResult
    market_data: MarketData
    report:      ReportResult


class ChatResponse(BaseModel):
    reply:      str
    mode:       str  # "live" | "error"
    message_id: Optional[int] = None


class FeedbackRequest(BaseModel):
    message_id: int
    feedback:   str  # 'like' or 'dislike'


class SessionInfo(BaseModel):
    """Lightweight session summary for listing in sidebar."""
    session_id: str
    title:      str
    created_at: str
    message_count: int = 0


class SessionTitleUpdate(BaseModel):
    title: str


class HealthResponse(BaseModel):
    status:      str
    environment: str


class ErrorResponse(BaseModel):
    detail: str
