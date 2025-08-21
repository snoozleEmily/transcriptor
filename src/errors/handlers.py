import functools
import speech_recognition as sr
from typing import Any, Callable


from .debug import debug
from .func_printer import get_func_call
from .logging import log_unexpected_error
from .exceptions import AppError, ErrorCode, FileError, TranscriptionError



def catch_errors(func: Callable) -> Callable:
    """
    Enhanced error handling decorator with file operation support
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        debug.dprint(get_func_call(func, args, kwargs)) # Get details before execution
        
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
            
        except PermissionError as e:
            log_unexpected_error(e)
            raise FileError.pdf_permission_denied(str(e.filename), e) from e
            
        except FileNotFoundError as e:
            log_unexpected_error(e)
            raise FileError(
                code=ErrorCode.FILE_ERROR,
                message="File or directory not found",
                context={"path": str(e.filename)}
            ) from e
            
        except OSError as e:
            log_unexpected_error(e)
            raise FileError(
                code=ErrorCode.FILE_ERROR,
                message="OS error during file operation",
                context={"error": str(e)}
            ) from e
            
        except Exception as e:
            log_unexpected_error(e)
            raise AppError(
                code=ErrorCode.UNEXPECTED_ERROR,
                message=f"Unexpected error: {str(e)}"
            ) from e

    return wrapper