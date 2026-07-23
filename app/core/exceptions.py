"""
Domain-level exceptions. Routers/services raise these; a single exception
handler in app.main maps each type to the right HTTP status code. This keeps
'what went wrong' (here) separate from 'what HTTP status that means' (main.py).
"""


class AppError(Exception):
    """Base class for all expected, handled application errors."""

    status_code: int = 500

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnsupportedFileTypeError(AppError):
    status_code = 400


class FileTooLargeError(AppError):
    status_code = 413


class FileParsingError(AppError):
    status_code = 422


class SessionNotFoundError(AppError):
    status_code = 404


class AnalysisNotRunError(AppError):
    status_code = 409


class NoAudioContentError(AppError):
    status_code = 422
