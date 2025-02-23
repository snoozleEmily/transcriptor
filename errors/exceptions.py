from enum import Enum
from typing import Optional, Dict, Any

class ErrorCode(Enum):
    NO_SPEECH = "no_speech_detected"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INVALID_INPUT = "invalid_input"
    FFMPEG_ERROR = "ffmpeg_error"
    UNKNOWN_ERROR = "unknown_error"
    UNEXPECTED_ERROR = "unexpected_error"

class AppError(Exception):
    """Base application exception type"""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.context = context or {}
        super().__init__(message)

class FFmpegError(AppError):
    """FFmpeg-related operation errors"""
    
    @classmethod
    def from_ffmpeg_output(cls, output: str) -> "FFmpegError":
        return cls(
            code=ErrorCode.FFMPEG_ERROR,
            message="FFmpeg processing failed",
            context={"ffmpeg_output": output}
        )

class TranscriptionError(AppError):
    """Transcription service errors"""
    
    @classmethod
    def from_whisper_error(cls, error: Exception) -> "TranscriptionError":
        return cls(
            code=ErrorCode.SERVICE_UNAVAILABLE,
            message="Transcription service error",
            context={"original_error": str(error)}
        )