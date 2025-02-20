import speech_recognition as sr
from typing import Callable, Any

class CustomError(Exception):
    """Base class for custom exceptions."""
    pass

class FfmpegMissingError(CustomError):
    """Raised when ffmpeg is missing."""
    def __init__(self, message: str = "ffmpeg not found. Install from https://ffmpeg.org/"):
        super().__init__(message)

class AudioExtractionError(CustomError):
    """Raised when audio extraction fails."""
    def __init__(self, message: str = "Audio extraction failed."):
        super().__init__(message)

class TranscriptionError(CustomError):
    """Raised when transcription fails."""
    def __init__(self, message: str = "Transcription failed."):
        super().__init__(message)

class FileSaveError(CustomError):
    """Raised when file saving fails."""
    def __init__(self, message: str = "Failed to save transcription."):
        super().__init__(message)

def transcription_error_handler(func: Callable) -> Callable:
    """
    Decorator to handle transcription errors with constant time complexity O(1).

    Wraps the decorated transcription function to intercept specific exceptions
    and re-raise them as custom TranscriptionError instances.
    """
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except sr.UnknownValueError:
            raise TranscriptionError("Speech was unintelligible")
        except Exception as e:
            raise TranscriptionError(f"Transcription error: {e}")
    return wrapper

def handle_error(exception: Exception) -> str:
    """
    Centralized error handler that maps custom exceptions to their messages.

    Complexity: O(1) since it performs a fixed number of type checks.
    """
    error_mapping = {
        FfmpegMissingError: "ffmpeg not found. Install from https://ffmpeg.org/",
        AudioExtractionError: "Audio extraction failed.",
        TranscriptionError: "Transcription failed.",
        FileSaveError: "Failed to save transcription."
    }
    
    for error_type, default_message in error_mapping.items():
        if isinstance(exception, error_type):
            # Return the actual message from the exception (allows custom messages).
            return str(exception)
    
    return "An unknown error occurred."
