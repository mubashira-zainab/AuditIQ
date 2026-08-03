"""
Central application configuration. Values load from environment variables
and an optional `.env` file (see `.env.example`). Nothing is hardcoded
elsewhere in the app -- if a value can plausibly change per-environment,
it lives here.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_name:    str = "AuditIQ API"
    environment: str = "development"   # development | production
    log_level:   str = "INFO"

    # --- CORS ---
    allowed_origins: str = "*"

    # --- Storage ---
    storage_dir:          Path = Path(__file__).resolve().parent.parent / "storage"
    max_upload_mb:        int  = 15
    session_ttl_minutes:  int  = 120

    # --- Auth (JWT) ---
    jwt_secret:       str = "auditiq-super-secret-key-change-in-production"
    jwt_algorithm:    str = "HS256"
    jwt_expire_hours: int = 720        # 30 days

    # --- AI pipeline ---
    groq_api_key:            str | None = None
    groq_model:              str = "llama-3.3-70b-versatile"
    groq_timeout_seconds:    int = 45
    default_forecast_horizon: int = 3
    max_forecast_horizon:    int = 12

    # --- Audio ---
    audio_default_speed: float = 1.25
    audio_max_chars:     int   = 1000

    @property
    def allowed_origins_list(self) -> list[str]:
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance -- read once, reused everywhere via DI."""
    return Settings()
