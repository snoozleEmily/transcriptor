import os
from typing import Any, Callable


from .exceptions import FileError, ErrorCode



def _sanitize_path(path: str) -> str:
    """Sanitize file paths to show only filename"""
    try:
        if isinstance(path, str) and (
            os.path.sep in path
            or any(
                path.lower().endswith(ext) 
                for ext 
                in (".mp4", ".avi", ".mov", ".mkv")
            )
        ):
            return f"[FILENAME]: {os.path.basename(path)}"
        return str(path)

    except Exception:
        raise FileError(code=ErrorCode.FILE_ERROR, message="Video path not found")


def _format_config(config: Any) -> list[str]:
    """Format configuration content for display"""
    if hasattr(config, "__dict__"):
        return [
            f"  Config: {type(config).__name__}",
            f"    - Categories: {getattr(config, 'categories', 'N/A')}",
            f"    - Types: {getattr(config, 'types', 'N/A')}",
            f"    - Words: {getattr(config, 'words', 'N/A')}",
        ]
    elif isinstance(config, dict):
        return [
            f"  Config: dict",
            f"    - Categories: {config.get('categories', 'N/A')}",
            f"    - Types: {config.get('types', 'N/A')}",
            f"    - Words: {config.get('words', 'N/A')}",
        ]
    
    return [f"  Config: {str(config)}"]


def get_func_call(func: Callable, args: tuple, kwargs: dict) -> str:
    """
    Formats function call information with proper argument handling
    """
    output = [f"\n{'='*50}", f"Function Call: {func.__name__}", f"{'-'*50}"]

    # Positional arguments
    if args:
        output.append("Positional Arguments:")
        for i, arg in enumerate(args, 1):
            display = _sanitize_path(arg)
            output.append(f"  Arg {i}: {type(arg).__name__} = {display}")

    # Keyword arguments
    if kwargs:
        output.append("Keyword Arguments:")
        for key, value in kwargs.items():
            if key == "config_params":
                output.extend(_format_config(value))
            else:
                display = (
                    _sanitize_path(value) if isinstance(value, str) else str(value)
                )
                output.append(f"  {key}: {type(value).__name__} = {display}")

    output.append(f"{'='*50}\n")
    return "\n".join(output)
