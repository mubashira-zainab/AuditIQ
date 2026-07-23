"""
Turns report text into a spoken briefing. Speed-up via ffmpeg is best-effort:
if ffmpeg isn't on PATH, we silently serve the normal-speed file instead of
failing the request -- a missing optional tool shouldn't break a working feature.
"""
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path

from app.core.exceptions import NoAudioContentError

logger = logging.getLogger(__name__)


def _clean_for_speech(text: str, max_chars: int) -> str:
    cleaned = re.sub(r"[*#_]", "", text).strip()
    return cleaned[:max_chars]


def generate_narration(text: str, language: str, session_dir: Path, speed: float, max_chars: int) -> Path:
    """
    Synthesizes `text` to an mp3 in `session_dir`, sped up by `speed` if ffmpeg
    is available. Returns the path to the final playable file.
    """
    from gtts import gTTS  # imported here to keep import-time side effects local to this function

    clean_text = _clean_for_speech(text, max_chars)
    if not clean_text:
        raise NoAudioContentError("No report text available to narrate.")

    lang_code = "ur" if language == "Urdu" else "en"

    raw_path = session_dir / "narration.mp3"
    gTTS(text=clean_text, lang=lang_code, slow=False).save(str(raw_path))

    if shutil.which("ffmpeg") is None:
        logger.info("ffmpeg not found on PATH; serving narration at normal speed.")
        return raw_path

    fast_path = session_dir / "narration_fast.mp3"
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", str(raw_path), "-filter:a", f"atempo={speed}", str(fast_path)],
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0 and fast_path.exists():
            return fast_path
        logger.info("ffmpeg speed-up failed (code %s); serving normal speed.", result.returncode)
    except Exception as e:
        logger.info("ffmpeg speed-up raised an exception; serving normal speed: %s", e)

    return raw_path
