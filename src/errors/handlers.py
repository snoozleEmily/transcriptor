import functools
import speech_recognition as sr
from typing import Any, Callable


from .func_printer import get_func_call
from .logging import log_unexpected_error
from .exceptions import AppError, ErrorCode, TranscriptionError



def catch_errors(func: Callable) -> Callable:
    """
    Error handling decorator for controller methods.
    
    Catches specific speech recognition errors and general exceptions, converting them
    to application-specific error types while preserving the original traceback.
    Also prints detailed function call information before execution.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        # Print function call details before execution
        print(get_func_call(func, args, kwargs))
        
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
    """
    Serialize exception details for API/client consumption.
    
    Returns:
        dict: Structured error information containing error code, message, 
              and context details.
    """
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