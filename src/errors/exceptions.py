from enum import Enum
from typing import Optional, Dict, Any

class ErrorCode(Enum):
    NO_SPEECH = "no_speech_detected"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INVALID_INPUT = "invalid_input"
    FILE_ERROR = "file_error"
    FFMPEG_ERROR = "ffmpeg_error"
    UNKNOWN_ERROR = "unknown_error"
    UNEXPECTED_ERROR = "unexpected_error"


class AppError(Exception):
    """Base application exception type with emoji support"""
    # Emoji mapping for different error types
    EMOJI_MAP = {
        ErrorCode.FILE_ERROR: "📄",
        ErrorCode.FFMPEG_ERROR: "🎬",
        ErrorCode.SERVICE_UNAVAILABLE: "🛠️",
        ErrorCode.INVALID_INPUT: "❌",
        ErrorCode.NO_SPEECH: "🔇",
        ErrorCode.UNEXPECTED_ERROR: "💥",
        ErrorCode.UNKNOWN_ERROR: "❓"
    }
    
    DEFAULT_EMOJI = "🛑"  # Fallback emoji

    def __init__(
        self, code: ErrorCode, message: str, context: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = self._format_message(message)
        self.context = context or {}
        super().__init__(self.message)

    def _format_message(self, message: str) -> str:
        """Formats the message with appropriate emoji"""
        emoji = self.EMOJI_MAP.get(self.code, self.DEFAULT_EMOJI)
        return f"{emoji} {message}"


class FileError(AppError):
    """File operation errors"""

    @classmethod
    def save_failed(cls, error: Exception) -> "FileError":
        return cls(
            code=ErrorCode.FILE_ERROR,
            message="Failed to save file",
            context={"original_error": str(error)},
        )

    @classmethod
    def empty_text(cls) -> "FileError":
        return cls(
            code=ErrorCode.FILE_ERROR,
            message="Empty transcription text",
            context={},
        )


class FFmpegError(AppError):
    """FFmpeg-related operation errors"""

    @classmethod
    def from_ffmpeg_output(cls, output: str) -> "FFmpegError":
        return cls(
            code=ErrorCode.FFMPEG_ERROR,
            message="FFmpeg processing failed",
            context={"ffmpeg_output": output},
        )


class TranscriptionError(AppError):
    """Transcription service errors"""

    @classmethod
    def generic_error(cls, message: str, error: Exception) -> "TranscriptionError":
        return cls(
            code=ErrorCode.UNEXPECTED_ERROR,
            message=message,
            context={"original_error": str(error)},
        )

    @classmethod
    def from_whisper_error(cls, error: Exception) -> "TranscriptionError":
        return cls(
            code=ErrorCode.SERVICE_UNAVAILABLE,
            message="Transcription service error",
            context={"original_error": str(error)},
        )

    @classmethod
    def load_failed(cls, error: Exception = None) -> "TranscriptionError":
        return cls(
            code=ErrorCode.SERVICE_UNAVAILABLE,
            message="Failed to load audio file",
            context={"original_error": str(error) if error else ""},
        )

    @classmethod
    def empty_audio(cls) -> "TranscriptionError":
        return cls(
            code=ErrorCode.INVALID_INPUT,
            message="Empty audio file",
            context={}
        )

    @classmethod
    def preprocessing_failed(cls, error: Exception = None) -> "TranscriptionError":
        return cls(
            code=ErrorCode.UNEXPECTED_ERROR,
            message="Audio preprocessing failed",
            context={"original_error": str(error) if error else ""},
        )

    @classmethod
    def invalid_model(cls) -> "TranscriptionError":
        return cls(
            code=ErrorCode.INVALID_INPUT,
            message="Invalid model size",
            context={}
        )

    @classmethod
    def no_speech(cls) -> "TranscriptionError":
        return cls(
            code=ErrorCode.NO_SPEECH,
            message="No speech detected in the audio",
            context={},
        )

    @classmethod
    def no_result(cls) -> "TranscriptionError":
        return cls(
            code=ErrorCode.NO_SPEECH,
            message="No transcription results returned",
            context={},
        )

    @classmethod
    def invalid_format(cls) -> "TranscriptionError":
        return cls(
            code=ErrorCode.UNEXPECTED_ERROR,
            message="Invalid result format from transcription service",
            context={},
        )

    @classmethod
    def missing_model_config(cls, model: str, config_type: str) -> "TranscriptionError":
        return cls(
            code=ErrorCode.INVALID_INPUT,
            message=f"Missing {config_type} configuration for model '{model}'",
            context={
                "model": model,
                "config_type": config_type
            }
        )

    @classmethod
    def invalid_model_size(cls, model: str) -> "TranscriptionError":
        return cls(
            code=ErrorCode.INVALID_INPUT,
            message=f"Invalid model size: '{model}'",
            context={
                "model": model
            }
        )