"""Free-form chat endpoint — real conversation with memory, history management, and feedback."""
from fastapi import APIRouter, Depends, Form, HTTPException, Body
from typing import List
import os

from app.config import Settings, get_settings
from app.dependencies import get_session_store
from app.schemas import (
    ChatResponse, ReportLanguage, FeedbackRequest,
    SessionInfo, SessionTitleUpdate
)
from app.services.ai_pipeline import answer_chat_message
from app.services.file_generator import process_dynamic_files
from app.services.session_store import SessionStore

router = APIRouter(tags=["chat"])


# ─── SEND MESSAGE ─────────────────────────────────────────────────────────────

@router.post("/api/chat", response_model=ChatResponse)
async def chat(
    message:    str = Form(...),
    session_id: str = Form(""),
    username:   str = Form(""),
    language:   ReportLanguage = Form(ReportLanguage.english),
    api_key:    str = Form(""),
    settings:   Settings = Depends(get_settings),
    store:      SessionStore = Depends(get_session_store),
) -> ChatResponse:

    context = ""
    history = []

    if session_id:
        try:
            session  = store.get(session_id)
            context  = session.upload.get("full_text") or session.upload.get("preview_text", "")
            history  = session.extra.get("messages", [])
            store.add_message(session_id, "user", message)

            # Auto-set title from first user message if not yet set
            if not session.title or session.title in ("", "New Chat"):
                auto_title = message[:60].strip()
                store.update_title(session_id, auto_title)

        except Exception:
            context = ""

    user_prefix = f"User Name: {username}. " if username else ""
    full_message_context = f"{user_prefix}{message}"

    result = answer_chat_message(
        message=full_message_context,
        context=context,
        language=language.value,
        api_key=api_key.strip() or None,
        settings=settings,
        history=history,
    )

    host_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    if "reply" in result:
        result["reply"] = process_dynamic_files(result["reply"], host_url)

    message_id = None
    if session_id and result.get("mode") != "error" and "reply" in result:
        try:
            message_id = store.add_message(session_id, "ai", result["reply"])
            result["message_id"] = message_id
        except Exception:
            pass

    return ChatResponse(**result)


# ─── FEEDBACK ─────────────────────────────────────────────────────────────────

@router.post("/api/chat/feedback")
async def chat_feedback(
    req:   FeedbackRequest,
    store: SessionStore = Depends(get_session_store),
):
    success = store.update_message_feedback(req.message_id, req.feedback)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")

    reply = (
        "Thank you for the feedback. I'll work on improving my responses."
        if req.feedback == "dislike"
        else "Thank you! Glad I could help."
    )
    return {"status": "success", "reply": reply}


# ─── GET HISTORY (single session) ─────────────────────────────────────────────

@router.get("/api/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    store:      SessionStore = Depends(get_session_store),
):
    try:
        session = store.get(session_id)
        return {
            "session_id": session.session_id,
            "title":      session.title,
            "upload":     session.upload,
            "analysis":   session.analysis,
            "messages":   session.extra.get("messages", []),
        }
    except Exception:
        return {
            "session_id": session_id,
            "title":      "",
            "upload":     None,
            "analysis":   None,
            "messages":   [],
            "recovered":  True,
        }


# ─── LIST SESSIONS FOR USER ───────────────────────────────────────────────────

@router.get("/api/chat/sessions/{username}", response_model=List[SessionInfo])
async def list_user_sessions(
    username: str,
    store:    SessionStore = Depends(get_session_store),
):
    """Return all sessions for a user (sidebar history list)."""
    sessions = store.list_sessions_for_user(username)
    return [SessionInfo(**s) for s in sessions]


# ─── UPDATE SESSION TITLE ─────────────────────────────────────────────────────

@router.patch("/api/chat/session/{session_id}/title")
async def update_session_title(
    session_id: str,
    body:       SessionTitleUpdate,
    store:      SessionStore = Depends(get_session_store),
):
    success = store.update_title(session_id, body.title)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "updated", "title": body.title}


# ─── DELETE SINGLE SESSION ────────────────────────────────────────────────────

@router.delete("/api/chat/session/{session_id}")
async def delete_session(
    session_id: str,
    store:      SessionStore = Depends(get_session_store),
):
    deleted = store.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted", "session_id": session_id}


# ─── DELETE ALL SESSIONS FOR USER ─────────────────────────────────────────────

@router.delete("/api/chat/sessions/{username}")
async def delete_all_user_sessions(
    username: str,
    store:    SessionStore = Depends(get_session_store),
):
    """Delete every conversation for a user (clear history)."""
    count = store.delete_all_for_user(username)
    return {"status": "cleared", "deleted_count": count}