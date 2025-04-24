import functools
import speech_recognition as sr
from typing import Callable, Any


from .logging import log_unexpected_error
from .exceptions import (
    AppError,
    TranscriptionError,
    ErrorCode
)



def catch_errors(func: Callable) -> Callable:
    """Error handling decorator for controller methods"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs) -> Any: 
        print(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}") # Debug
        try:
            return func(self, *args, **kwargs)
            
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