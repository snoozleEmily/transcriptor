from .exceptions import (
    Errors,
    FFmpegError,
    TranscriptionError,
    FileError
)

from .handlers import (
    catch_errors,
    transcribe_errors,
    format_error
)

from .logging import (
    configure_logging,
    log_unexpected_error
)

__all__ = [
    "Errors",
    "FFmpegError",
    "TranscriptionError",
    "FileError"
]