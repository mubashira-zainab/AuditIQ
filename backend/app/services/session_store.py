"""
In-memory session store.

This is deliberately simple: a single-process dict guarded by a lock, with
lazy TTL expiry. It's the right amount of infrastructure for a local/single-
instance MVP. If this ever needs to run multi-process or survive restarts,
swap this class for a Redis-backed implementation -- nothing outside this
file needs to change, since routers only ever talk to `SessionStore`.
"""
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.core.exceptions import SessionNotFoundError


@dataclass
class Session:
    session_id: str
    created_at: float
    file_path: str
    upload: dict[str, Any]
    analysis: dict[str, Any] | None = None
    language: str = "English"
    extra: dict[str, Any] = field(default_factory=dict)


class SessionStore:
    def __init__(self, ttl_minutes: int = 120):
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()
        self._ttl_seconds = ttl_minutes * 60

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())

    def create(self, session_id: str, file_path: str, upload: dict[str, Any]) -> Session:
        session = Session(
            session_id=session_id,
            created_at=time.time(),
            file_path=file_path,
            upload=upload,
        )
        with self._lock:
            self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> Session:
        with self._lock:
            session = self._sessions.get(session_id)

        if session is None:
            raise SessionNotFoundError(f"No session found for id '{session_id}'. Upload a file first.")

        if time.time() - session.created_at > self._ttl_seconds:
            self.delete(session_id)
            raise SessionNotFoundError(f"Session '{session_id}' expired. Upload the file again.")

        return session

    def update(self, session_id: str, **fields: Any) -> Session:
        session = self.get(session_id)
        for key, value in fields.items():
            setattr(session, key, value)
        return session

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def sweep_expired(self) -> int:
        """Remove all expired sessions. Returns the number removed."""
        now = time.time()
        with self._lock:
            expired = [sid for sid, s in self._sessions.items() if now - s.created_at > self._ttl_seconds]
            for sid in expired:
                del self._sessions[sid]
        return len(expired)


# Single shared instance for the process -- imported by routers via app.dependencies.
session_store = SessionStore()
