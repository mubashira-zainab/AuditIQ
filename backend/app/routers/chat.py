"""Free-form chat endpoint -- lets the frontend's message box hold a real conversation."""
from fastapi import APIRouter, Depends, Form, HTTPException, Body
import os

from app.config import Settings, get_settings
from app.dependencies import get_session_store
from app.schemas import ChatResponse, ReportLanguage, FeedbackRequest
from app.services.ai_pipeline import answer_chat_message
from app.services.file_generator import process_dynamic_files
from app.services.session_store import SessionStore

router = APIRouter(tags=["chat"])

@router.post("/api/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(...),
    session_id: str = Form(""),
    username: str = Form(""),
    language: ReportLanguage = Form(ReportLanguage.english),
    api_key: str = Form(""),
    settings: Settings = Depends(get_settings),
    store: SessionStore = Depends(get_session_store),
) -> ChatResponse:
    context = ""
    history = []
    
    if session_id:
        try:
            session = store.get(session_id)
            context = session.upload.get("full_text") or session.upload.get("preview_text", "")
            history = session.extra.get("messages", [])
            # Persist user message
            store.add_message(session_id, "user", message)
        except Exception:
            context = ""

    # Include user context / profile name if provided
    user_prefix = f"User Name: {username}. " if username else ""
    full_message_context = f"{user_prefix}{message}"

    result = answer_chat_message(
        message=full_message_context, 
        context=context, 
        language=language.value, 
        api_key=api_key.strip() or None, 
        settings=settings,
        history=history
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


@router.post("/api/chat/feedback")
async def chat_feedback(
    req: FeedbackRequest,
    store: SessionStore = Depends(get_session_store),
):
    success = store.update_message_feedback(req.message_id, req.feedback)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
        
    # Professional reply logic based on feedback
    if req.feedback == "dislike":
        reply = "Thank you for the feedback. I'll take this into account and improve my mistakes."
    else:
        reply = "Thank you! I'm glad I could help."
        
    return {"status": "success", "reply": reply}


@router.get("/api/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    store: SessionStore = Depends(get_session_store),
):
    try:
        session = store.get(session_id)
        return {
            "session_id": session.session_id,
            "upload": session.upload,
            "analysis": session.analysis,
            "messages": session.extra.get("messages", [])
        }
    except Exception as e:
        # Graceful fallback instead of 404 crash
        return {
            "session_id": session_id,
            "upload": None,
            "analysis": None,
            "messages": [],
            "recovered": True
        }