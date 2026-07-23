"""Shared FastAPI dependencies, injected into routers via `Depends(...)`."""
from app.config import Settings, get_settings  # re-exported for convenience
from app.services.session_store import SessionStore, session_store


def get_session_store() -> SessionStore:
    return session_store


__all__ = ["get_settings", "Settings", "get_session_store", "SessionStore"]
