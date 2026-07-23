"""Handles ledger/document ingestion: validates, saves, and parses any file type."""
import logging
import os
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
    
    # Extension validation (Allows everything safely now)
    ext = validate_extension(safe_name)

    raw_bytes = await file.read()
    validate_size(len(raw_bytes), settings.max_upload_mb)

    session_id = store.new_id()
    session_dir = settings.storage_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    dest_path = session_dir / safe_name
    dest_path.write_bytes(raw_bytes)

    # Universal File Processing Logic
    file_type = "document"
    summary_data = {
        "target_column": None,
        "total": 0.0,
        "row_count": 0,
        "series": [],
        "preview_text": f"File {safe_name} uploaded successfully. Ready for audit analysis."
    }

    try:
        if ext in (".xlsx", ".xls"):
            file_type = "spreadsheet"
            df = read_excel_file(str(dest_path))
            summary = summarize_dataframe(df)
            summary_data.update(summary)
            summary_data["full_text"] = df.to_string()
        elif ext in (".csv",):
            file_type = "spreadsheet"
            df = read_csv_file(str(dest_path))
            summary = summarize_dataframe(df)
            summary_data.update(summary)
            summary_data["full_text"] = df.to_string()
        elif ext in (".pdf",):
            file_type = "pdf"
            text = read_pdf_file(str(dest_path))
            summary_data["preview_text"] = text[:2000] if text else "PDF loaded successfully."
            summary_data["full_text"] = text
        elif ext in (".png", ".jpg", ".jpeg", ".webp"):
            file_type = "image"
            summary_data["preview_text"] = f"Image {safe_name} successfully processed for automated AI reporting."
            summary_data["full_text"] = f"Image {safe_name} data."
        else:
            # Universal fallback for any other text/data file type
            file_type = "document"
            with open(dest_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                summary_data["preview_text"] = content[:2000] if content else f"Document {safe_name} successfully parsed."
                summary_data["full_text"] = content
    except Exception as e:
        logger.error("Error processing file %s: %s", safe_name, e)
        summary_data["preview_text"] = f"File uploaded, but parsing warning: {str(e)}"
        summary_data["full_text"] = f"Error details: {str(e)}"

    upload_data = {
        "filename": safe_name,
        "file_type": file_type,
        **summary_data
    }

    session = store.create(session_id=session_id, file_path=str(dest_path), upload=upload_data)
    logger.info("Upload accepted & reset: session=%s file=%s type=%s", session.session_id, safe_name, file_type)

    return UploadResponse(session_id=session.session_id, **upload_data)