"""
Persistent session store using SQLAlchemy and SQLite.
Supports: create, get, update, delete, delete_all, list_sessions, add_message, update_title.
"""
import uuid
import time
from dataclasses import dataclass, field
from typing import Any, List

from app.core.exceptions import SessionNotFoundError
from app.db import SessionLocal
from app.models import DBSession, DBMessage


@dataclass
class Session:
    session_id: str
    created_at: float
    file_path:  str
    upload:     dict[str, Any]
    analysis:   dict[str, Any] | None = None
    language:   str = "English"
    title:      str = ""
    username:   str = ""
    extra:      dict[str, Any] = field(default_factory=dict)


class SessionStore:
    def __init__(self, ttl_minutes: int = 120):
        # TTL not used with persistent DB, kept for compatibility
        pass

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())

    # ─── CREATE ───────────────────────────────────────────────────────────────

    def create(self, session_id: str, file_path: str, upload: dict[str, Any],
               username: str = "", title: str = "") -> Session:
        db = SessionLocal()
        try:
            db_sess = DBSession(
                session_id=session_id,
                file_path=file_path,
                upload_data=upload,
                username=username,
                title=title or upload.get("filename", "New Chat"),
            )
            db.add(db_sess)
            db.commit()
            return self.get(session_id)
        finally:
            db.close()

    # ─── GET ──────────────────────────────────────────────────────────────────

    def get(self, session_id: str) -> Session:
        db = SessionLocal()
        try:
            db_sess = db.query(DBSession).filter(
                DBSession.session_id == session_id
            ).first()
            if not db_sess:
                raise SessionNotFoundError(
                    f"No session found for id '{session_id}'. Upload a file first."
                )

            messages = [
                {
                    "id":         m.id,
                    "role":       m.role,
                    "content":    m.content,
                    "feedback":   m.feedback,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in db_sess.messages
            ]

            return Session(
                session_id=db_sess.session_id,
                created_at=db_sess.created_at.timestamp() if db_sess.created_at else time.time(),
                file_path=db_sess.file_path or "",
                upload=db_sess.upload_data or {},
                analysis=db_sess.analysis_data,
                language=db_sess.language or "English",
                title=db_sess.title or "",
                username=db_sess.username or "",
                extra={"messages": messages},
            )
        finally:
            db.close()

    # ─── UPDATE ───────────────────────────────────────────────────────────────

    def update(self, session_id: str, **fields: Any) -> Session:
        db = SessionLocal()
        try:
            db_sess = db.query(DBSession).filter(
                DBSession.session_id == session_id
            ).first()
            if not db_sess:
                raise SessionNotFoundError(f"No session found for id '{session_id}'.")

            if "upload"   in fields: db_sess.upload_data   = fields["upload"]
            if "analysis" in fields: db_sess.analysis_data = fields["analysis"]
            if "language" in fields: db_sess.language       = fields["language"]
            if "title"    in fields: db_sess.title          = fields["title"]
            if "username" in fields: db_sess.username       = fields["username"]

            db.commit()
            return self.get(session_id)
        finally:
            db.close()

    # ─── UPDATE TITLE ─────────────────────────────────────────────────────────

    def update_title(self, session_id: str, title: str) -> bool:
        db = SessionLocal()
        try:
            db_sess = db.query(DBSession).filter(
                DBSession.session_id == session_id
            ).first()
            if not db_sess:
                return False
            db_sess.title = title[:120]   # cap at 120 chars
            db.commit()
            return True
        finally:
            db.close()

    # ─── DELETE ONE ───────────────────────────────────────────────────────────

    def delete(self, session_id: str) -> bool:
        db = SessionLocal()
        try:
            db_sess = db.query(DBSession).filter(
                DBSession.session_id == session_id
            ).first()
            if db_sess:
                db.delete(db_sess)
                db.commit()
                return True
            return False
        finally:
            db.close()

    # ─── DELETE ALL FOR USER ──────────────────────────────────────────────────

    def delete_all_for_user(self, username: str) -> int:
        """Delete every session belonging to *username*. Returns count deleted."""
        db = SessionLocal()
        try:
            sessions = db.query(DBSession).filter(
                DBSession.username == username
            ).all()
            count = len(sessions)
            for s in sessions:
                db.delete(s)
            db.commit()
            return count
        finally:
            db.close()

    # ─── LIST SESSIONS FOR USER ───────────────────────────────────────────────

    def list_sessions_for_user(self, username: str) -> List[dict]:
        """Return lightweight session info list (newest first)."""
        db = SessionLocal()
        try:
            sessions = (
                db.query(DBSession)
                .filter(DBSession.username == username)
                .order_by(DBSession.created_at.desc())
                .all()
            )
            result = []
            for s in sessions:
                msg_count = db.query(DBMessage).filter(
                    DBMessage.session_id == s.session_id
                ).count()
                result.append({
                    "session_id":    s.session_id,
                    "title":         s.title or s.upload_data.get("filename", "Chat") if s.upload_data else "Chat",
                    "created_at":    s.created_at.isoformat() if s.created_at else "",
                    "message_count": msg_count,
                })
            return result
        finally:
            db.close()

    # ─── MESSAGES ─────────────────────────────────────────────────────────────

    def add_message(self, session_id: str, role: str, content: str) -> int:
        db = SessionLocal()
        try:
            msg = DBMessage(session_id=session_id, role=role, content=content)
            db.add(msg)
            db.commit()
            db.refresh(msg)
            return msg.id
        finally:
            db.close()

    def update_message_feedback(self, message_id: int, feedback: str) -> bool:
        db = SessionLocal()
        try:
            msg = db.query(DBMessage).filter(DBMessage.id == message_id).first()
            if msg:
                msg.feedback = feedback
                db.commit()
                return True
            return False
        finally:
            db.close()

    def sweep_expired(self) -> int:
        return 0  # No expiry for persistent store


# Single shared instance
session_store = SessionStore()