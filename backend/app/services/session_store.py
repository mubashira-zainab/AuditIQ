"""
Persistent session store using SQLAlchemy and SQLite.
"""
import uuid
import time
from dataclasses import dataclass, field
from typing import Any

from app.core.exceptions import SessionNotFoundError
from app.db import SessionLocal
from app.models import DBSession, DBMessage


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
        # We don't use ttl in persistent DB, but keep signature for compatibility
        pass

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())

    def create(self, session_id: str, file_path: str, upload: dict[str, Any]) -> Session:
        db = SessionLocal()
        try:
            db_sess = DBSession(
                session_id=session_id,
                file_path=file_path,
                upload_data=upload
            )
            db.add(db_sess)
            db.commit()
            return self.get(session_id)
        finally:
            db.close()

    def get(self, session_id: str) -> Session:
        db = SessionLocal()
        try:
            db_sess = db.query(DBSession).filter(DBSession.session_id == session_id).first()
            if not db_sess:
                raise SessionNotFoundError(f"No session found for id '{session_id}'. Upload a file first.")
            
            messages = []
            for m in db_sess.messages:
                messages.append({
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "feedback": m.feedback,
                    "created_at": m.created_at.isoformat() if m.created_at else None
                })
                
            return Session(
                session_id=db_sess.session_id,
                created_at=db_sess.created_at.timestamp() if db_sess.created_at else time.time(),
                file_path=db_sess.file_path,
                upload=db_sess.upload_data or {},
                analysis=db_sess.analysis_data,
                language=db_sess.language,
                extra={"messages": messages}
            )
        finally:
            db.close()

    def update(self, session_id: str, **fields: Any) -> Session:
        db = SessionLocal()
        try:
            db_sess = db.query(DBSession).filter(DBSession.session_id == session_id).first()
            if not db_sess:
                raise SessionNotFoundError(f"No session found for id '{session_id}'.")
            
            if "upload" in fields:
                db_sess.upload_data = fields["upload"]
            if "analysis" in fields:
                db_sess.analysis_data = fields["analysis"]
            if "language" in fields:
                db_sess.language = fields["language"]
            
            db.commit()
            return self.get(session_id)
        finally:
            db.close()

    def delete(self, session_id: str) -> None:
        db = SessionLocal()
        try:
            db_sess = db.query(DBSession).filter(DBSession.session_id == session_id).first()
            if db_sess:
                db.delete(db_sess)
                db.commit()
        finally:
            db.close()

    def sweep_expired(self) -> int:
        return 0  # No expiry for persistent store
        
    def add_message(self, session_id: str, role: str, content: str):
        db = SessionLocal()
        try:
            msg = DBMessage(session_id=session_id, role=role, content=content)
            db.add(msg)
            db.commit()
            return msg.id
        finally:
            db.close()
            
    def update_message_feedback(self, message_id: int, feedback: str):
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

# Single shared instance
session_store = SessionStore()