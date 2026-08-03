"""
Database models — all SQLAlchemy ORM table definitions.

Tables:
  User      — registered users with hashed passwords
  DBSession — one chat session per conversation (with file upload)
  DBMessage — individual messages within a session
  Memory    — persistent AI memory facts per user
"""
from sqlalchemy import (
    Column, Integer, String, JSON, DateTime, ForeignKey,
    Text, Boolean, UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db import Base


# ─── USER ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email      = Column(String, unique=True, nullable=False, index=True)
    username   = Column(String, nullable=False, default="")
    password   = Column(String, nullable=False)          # bcrypt hash
    avatar     = Column(Text,   nullable=True,  default="")  # base64 or URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    sessions = relationship("DBSession", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory",    back_populates="user", cascade="all, delete-orphan")


# ─── SESSION (CHAT) ───────────────────────────────────────────────────────────

class DBSession(Base):
    __tablename__ = "sessions"

    session_id    = Column(String,  primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    username      = Column(String,  nullable=True, index=True)   # kept for backward compat
    title         = Column(String,  nullable=True, default="New Chat")
    file_path     = Column(String,  nullable=True)
    upload_data   = Column(JSON,    nullable=True)
    analysis_data = Column(JSON,    nullable=True)
    language      = Column(String,  default="English")
    is_pinned     = Column(Boolean, default=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user     = relationship("User",      back_populates="sessions")
    messages = relationship(
        "DBMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="DBMessage.created_at",
    )


# ─── MESSAGE ──────────────────────────────────────────────────────────────────

class DBMessage(Base):
    __tablename__ = "messages"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String,  ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    role       = Column(String,  nullable=False)     # 'user' | 'ai'
    content    = Column(Text,    nullable=False)
    feedback   = Column(String,  nullable=True)      # 'like' | 'dislike'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("DBSession", back_populates="messages")


# ─── MEMORY ───────────────────────────────────────────────────────────────────

class Memory(Base):
    __tablename__ = "memory"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    key        = Column(String,  nullable=False)   # e.g. 'company_name', 'financial_goal'
    value      = Column(Text,    nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="memories")

    __table_args__ = (
        UniqueConstraint("user_id", "key", name="uq_memory_user_key"),
    )
