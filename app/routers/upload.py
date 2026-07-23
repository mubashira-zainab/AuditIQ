"""Handles ledger/document ingestion: validates, saves, and parses the file."""
import logging

from fastapi import APIRouter, Depends, File, UploadFile

from app.config import Settings, get_settings
from app.core.security import sanitize_filename, validate_extension, validate_size
from app.dependencies import get_session_store
from app.schemas import UploadResponse
from app.services.data_processor import read_csv_file, read_excel_file, read_pdf_file, summarize_dataframe
from app.services.session_store import SessionStore

logger = logging.getLogger(__name__)
router = APIRouter(tags=["upload"])


@router.post("/api/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    store: SessionStore = Depends(get_session_store),
) -> UploadResponse:
    safe_name = sanitize_filename(file.filename or "upload")
    ext = validate_extension(safe_name)

    raw_bytes = await file.read()
    validate_size(len(raw_bytes), settings.max_upload_mb)

    session_id = store.new_id()
    session_dir = settings.storage_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    dest_path = session_dir / safe_name
    dest_path.write_bytes(raw_bytes)

    if ext in (".xlsx", ".csv"):
        df = read_excel_file(str(dest_path)) if ext == ".xlsx" else read_csv_file(str(dest_path))
        summary = summarize_dataframe(df)
        upload_data = {"filename": safe_name, "file_type": "spreadsheet", **summary}
    else:  # .pdf
        text = read_pdf_file(str(dest_path))
        upload_data = {
            "filename": safe_name,
            "file_type": "pdf",
            "target_column": None,
            "total": 0.0,
            "row_count": 0,
            "series": [],
            "preview_text": text[:2000],
        }

    session = store.create(session_id=session_id, file_path=str(dest_path), upload=upload_data)
    logger.info("Upload accepted: session=%s file=%s type=%s", session.session_id, safe_name, upload_data["file_type"])

    return UploadResponse(session_id=session.session_id, **upload_data)
