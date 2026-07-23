import pytest

from app.core.exceptions import FileTooLargeError, UnsupportedFileTypeError
from app.core.security import sanitize_filename, validate_extension, validate_size


def test_sanitize_filename_strips_path_traversal():
    assert sanitize_filename("../../etc/passwd") == "passwd"


def test_sanitize_filename_replaces_unsafe_chars():
    assert sanitize_filename("my report (final)!.xlsx") == "my_report_final_.xlsx"


def test_validate_extension_accepts_allowed_types():
    assert validate_extension("ledger.xlsx") == ".xlsx"
    assert validate_extension("data.CSV") == ".csv"


def test_validate_extension_rejects_disallowed_types():
    with pytest.raises(UnsupportedFileTypeError):
        validate_extension("script.exe")


def test_validate_size_rejects_oversized_file():
    with pytest.raises(FileTooLargeError):
        validate_size(size_bytes=20 * 1024 * 1024, max_mb=15)


def test_validate_size_accepts_within_limit():
    validate_size(size_bytes=1024, max_mb=15)  # should not raise
