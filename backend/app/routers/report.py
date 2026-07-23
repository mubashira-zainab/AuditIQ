"""Serves the compiled text report for a session that has completed analysis."""
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.core.exceptions import AnalysisNotRunError
from app.dependencies import get_session_store
from app.services.session_store import SessionStore

router = APIRouter(tags=["report"])


@router.get("/api/report/{session_id}/download")
async def download_report(session_id: str, store: SessionStore = Depends(get_session_store)) -> PlainTextResponse:
    session = store.get(session_id)
    if not session.analysis:
        raise AnalysisNotRunError("Run /api/analyze before downloading a report.")

    report = session.analysis["report"]
    filename = session.upload.get("filename", "upload")

    text = (
        f"AuditIQ Report -- {filename}\n"
        f"{'=' * 60}\n\n"
        f"COMPLIANCE REVIEW\n{'-' * 20}\n{report.get('compliance_report', '')}\n\n"
        f"FORECAST NARRATIVE\n{'-' * 20}\n{report.get('narrative_report', '')}\n"
    )

    return PlainTextResponse(
        text,
        headers={"Content-Disposition": "attachment; filename=auditiq_report.txt"},
    )
