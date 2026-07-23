"""Generates a spoken briefing from the most recent analysis of a session."""
from pathlib import Path

from fastapi import APIRouter, Depends, Form
from fastapi.responses import FileResponse

from app.config import Settings, get_settings
from app.core.exceptions import AnalysisNotRunError
from app.dependencies import get_session_store
from app.services.audio_service import generate_narration
from app.services.session_store import SessionStore

router = APIRouter(tags=["audio"])


@router.post("/api/audio")
async def generate_audio(
    session_id: str = Form(...),
    speed: float | None = Form(None),
    settings: Settings = Depends(get_settings),
    store: SessionStore = Depends(get_session_store),
) -> FileResponse:
    session = store.get(session_id)
    if not session.analysis:
        raise AnalysisNotRunError("Run /api/analyze before requesting audio.")

    text = session.analysis["report"].get("narrative_report", "")
    effective_speed = speed or settings.audio_default_speed
    session_dir = Path(session.file_path).parent

    output_path = generate_narration(
        text=text,
        language=session.language,
        session_dir=session_dir,
        speed=effective_speed,
        max_chars=settings.audio_max_chars,
    )

    return FileResponse(output_path, media_type="audio/mpeg", filename="auditiq_briefing.mp3")

@router.post("/api/audio-text")
async def generate_audio_text(
    text: str = Form(...),
    language: str = Form("English"),
    speed: float | None = Form(None),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    effective_speed = speed or settings.audio_default_speed
    
    # Use static directory for direct chat audio
    static_dir = Path(__file__).resolve().parent.parent.parent / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = generate_narration(
        text=text,
        language=language,
        session_dir=static_dir,
        speed=effective_speed,
        max_chars=settings.audio_max_chars,
    )

    return FileResponse(output_path, media_type="audio/mpeg", filename="auditiq_chat.mp3")
