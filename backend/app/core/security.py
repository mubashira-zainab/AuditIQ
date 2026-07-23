"""
Upload safety helpers: extension allow-listing, size limits, and filename
sanitization (never trust a client-supplied filename for building a path).
"""
import re
from pathlib import Path

from app.core.exceptions import FileTooLargeError, UnsupportedFileTypeError

ALLOWED_EXTENSIONS = {".xlsx", ".csv", ".pdf", ".txt", ".png", ".jpg", ".jpeg"}
_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    """
    Strip any directory components and unsafe characters so a client-supplied
    filename can never be used to write or read outside the intended folder.
    """
    name = Path(filename).name  # drops any path components (../, /etc/passwd, etc.)
    name = _SAFE_NAME_RE.sub("_", name)
    return name or "upload"


def validate_extension(filename: str) -> str:
    """Returns the lowercase extension if allowed, otherwise raises."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{ext or 'unknown'}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    return ext


def validate_size(size_bytes: int, max_mb: int) -> None:
    max_bytes = max_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise FileTooLargeError(f"File exceeds the {max_mb}MB upload limit.")
