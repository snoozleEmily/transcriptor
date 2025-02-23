from typing import Callable, Type, Any
import functools
import speech_recognition as sr

from .logging import log_unexpected_error
from .exceptions import (
    AppError,
    FFmpegError,
    TranscriptionError,
    ErrorCode
)

def error_handler(*error_types: Type[BaseException]) -> Callable:
    """Flexible error handling decorator factory"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            
            except error_types as e:
                raise  # Reraise already handled errors
                
            except sr.UnknownValueError as e:
                raise TranscriptionError(
                    code=ErrorCode.NO_SPEECH,
                    message="No speech detected in audio"
                ) from e
                
            except sr.RequestError as e:
                raise TranscriptionError(
                    code=ErrorCode.SERVICE_UNAVAILABLE,
                    message="Speech service unavailable"
                ) from e
                
            except Exception as e:
                log_unexpected_error(e)
                raise AppError(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"Unexpected error: {str(e)}"
                ) from e

        return wrapper
    return decorator

def format_error(error: Exception) -> dict:
    """Serialize error for API/client consumption"""
    if isinstance(error, AppError):
        return {
            "code": error.code.value,
            "message": error.message,
            "context": error.context
        }
        
    return {
        "code": ErrorCode.UNKNOWN_ERROR.value,
        "message": "An unknown error occurred",
        "context": str(error)
    }