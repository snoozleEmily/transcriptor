from typing import Callable, Dict, Any
import speech_recognition as sr


from .logging import log_unexpected_error
from .exceptions import Errors, FFmpegError




def catch_errors(func: Callable) -> Callable:
    """Global error catching decorator"""
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        
        except Errors as e:
            raise  # Already handled errors

        except Exception as e:
            log_unexpected_error(e)
            raise FFmpegError.generic_error(e)
        
    return wrapper

def transcribe_errors(func: Callable) -> Callable:
    """Handle transcription-specific errors"""
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        
        except sr.UnknownValueError as e:
            raise Errors.no_speech(e) from e
        
        except sr.RequestError as e:
            raise Errors.service_error(e) from e
        
        except Exception as e:
            raise Errors.generic_error(e) from e
        
    return wrapper

def format_error(error: Exception) -> dict:
    """Format error for display"""
    if isinstance(error, Errors):
        return {
            "code": error.code,
            "message": str(error)
        }
    else:
        return {
            "code": "UNKNOWN_ERROR",
            "message": str(error)
        }