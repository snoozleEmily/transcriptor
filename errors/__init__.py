from .exceptions import (
    AppError,
    FFmpegError,
    TranscriptionError,
    FileError,
    ErrorCode
)

from .handlers import (
    catch_errors,
    format_error
)

from .logging import (
    configure_logging,
    log_unexpected_error
)

__all__ = [
    # Error Types
    "AppError",
    "FFmpegError",
    "TranscriptionError",
    "FileError",
    
    # Error Codes
    "ErrorCode",
    
    # Handlers
    "catch_errors",
    "format_error",
    
    # Logging
    "configure_logging",
    "log_unexpected_error"
]