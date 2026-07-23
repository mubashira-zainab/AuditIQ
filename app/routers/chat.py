"""Free-form chat endpoint -- lets the frontend's message box hold a real conversation."""
from fastapi import APIRouter, Depends, Form

from app.config import Settings, get_settings
from app.dependencies import get_session_store
from app.schemas import ChatResponse, ReportLanguage
from app.services.ai_pipeline import answer_chat_message
from app.services.session_store import SessionStore

router = APIRouter(tags=["chat"])


@router.post("/api/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(...),
    session_id: str = Form(""),
    language: ReportLanguage = Form(ReportLanguage.english),
    api_key: str = Form(""),
    settings: Settings = Depends(get_settings),
    store: SessionStore = Depends(get_session_store),
) -> ChatResponse:
    context = ""
    if session_id:
        try:
            session = store.get(session_id)
            context = session.upload.get("preview_text", "")
        except Exception:
            context = ""  # unknown/expired session -- just chat without ledger context

    result = answer_chat_message(message, context, language.value, api_key.strip() or None, settings)
    return ChatResponse(**result)
