"""
Pydantic models for every request/response the API sends or accepts.
Keeping these centralized means FastAPI's auto-generated /docs are always
accurate and typos surface as validation errors instead of silent bugs.
"""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# ─── ENUMS ────────────────────────────────────────────────────────────────────

class ReportLanguage(str, Enum):
    english    = "English"
    roman_urdu = "Roman Urdu"
    urdu       = "Urdu"


# ─── AUTH ─────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email:    str
    username: str
    password: str

class UserLogin(BaseModel):
    email:    str
    password: str

class UserResponse(BaseModel):
    id:         int
    email:      str
    username:   str
    avatar:     Optional[str] = ""
    created_at: Optional[str] = None

class TokenResponse(BaseModel):
    token: str
    user:  UserResponse

class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    avatar:   Optional[str] = None


# ─── MEMORY ───────────────────────────────────────────────────────────────────

class MemoryItem(BaseModel):
    key:   str
    value: str

class MemoryResponse(BaseModel):
    items: List[MemoryItem]


# ─── UPLOAD ───────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    session_id:    str
    filename:      str
    file_type:     str                   # "spreadsheet" | "pdf" | "image" | "document"
    target_column: Optional[str] = None
    total:         float = 0.0
    row_count:     int   = 0
    series:        List[float] = Field(default_factory=list)
    preview_text:  str = ""


# ─── ANALYSIS ─────────────────────────────────────────────────────────────────

class ForecastResult(BaseModel):
    next_points: List[float]
    method:      str
    slope:       Optional[float] = None
    note:        Optional[str]   = None

class MarketData(BaseModel):
    resolved:            bool
    symbol_used:         Optional[str]         = None
    company_name:        Optional[str]         = None
    current_price:       Optional[float | str] = None
    market_cap:          Optional[float | str] = None
    pe_ratio:            Optional[float | str] = None
    fifty_two_week_high: Optional[float | str] = None
    fifty_two_week_low:  Optional[float | str] = None
    currency:            Optional[str]         = None
    error:               Optional[str]         = None

class ReportResult(BaseModel):
    compliance_report: str
    narrative_report:  str
    mode:              str              # "live" | "offline" | "error"
    error:             Optional[str] = None

class AnalyzeResponse(BaseModel):
    forecast:    ForecastResult
    market_data: MarketData
    report:      ReportResult


# ─── CHAT ─────────────────────────────────────────────────────────────────────

class ChatResponse(BaseModel):
    reply:      str
    mode:       str                     # "live" | "error"
    message_id: Optional[int] = None

class FeedbackRequest(BaseModel):
    message_id: int
    feedback:   str                     # 'like' | 'dislike'


# ─── SESSION ──────────────────────────────────────────────────────────────────

class SessionInfo(BaseModel):
    """Lightweight session summary for the sidebar history list."""
    session_id:    str
    title:         str
    created_at:    str
    message_count: int  = 0
    is_pinned:     bool = False

class SessionTitleUpdate(BaseModel):
    title: str

class SessionPinUpdate(BaseModel):
    is_pinned: bool


# ─── SYSTEM ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status:      str
    environment: str

class ErrorResponse(BaseModel):
    detail: str
