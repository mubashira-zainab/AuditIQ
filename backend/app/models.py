from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db import Base
from sqlalchemy.orm import relationship

class DBSession(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    file_path = Column(String, nullable=True)
    upload_data = Column(JSON, nullable=True)
    analysis_data = Column(JSON, nullable=True)
    language = Column(String, default="English")
    
    messages = relationship("DBMessage", back_populates="session", cascade="all, delete-orphan")

class DBMessage(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.session_id"))
    role = Column(String) # 'user' or 'ai'
    content = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    feedback = Column(String, nullable=True) # 'like', 'dislike'

    session = relationship("DBSession", back_populates="messages")
