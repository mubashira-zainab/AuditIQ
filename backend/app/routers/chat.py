"""Free-form chat endpoint -- lets the frontend's message box hold a real conversation."""
from fastapi import APIRouter, Depends, Form, HTTPException

from app.config import Settings, get_settings
from app.dependencies import get_session_store
from app.schemas import ChatResponse, ReportLanguage
from app.services.ai_pipeline import answer_chat_message
from app.services.file_generator import process_dynamic_files
from app.services.session_store import SessionStore
import os

router = APIRouter(tags=["chat"])


@router.post("/api/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(...),
    session_id: str = Form(""),
    username: str = Form(""),  # Added custom username form field parameter
    language: ReportLanguage = Form(ReportLanguage.english),
    api_key: str = Form(""),
    settings: Settings = Depends(get_settings),
    store: SessionStore = Depends(get_session_store),
) -> ChatResponse:
    context = ""
    if session_id:
        try:
            session = store.get(session_id)
            context = session.upload.get("full_text") or session.upload.get("preview_text", "")
        except Exception:
            context = ""  # unknown/expired session -- just chat without ledger context

    # Include user context / profile name if provided
    user_prefix = f"User Name: {username}. " if username else ""
    full_message_context = f"{user_prefix}{message}"

    result = answer_chat_message(full_message_context, context, language.value, api_key.strip() or None, settings)
    
    host_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    if "reply" in result:
        result["reply"] = process_dynamic_files(result["reply"], host_url)
        
    return ChatResponse(**result)

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
        raise HTTPException(status_code=404, detail=str(e))