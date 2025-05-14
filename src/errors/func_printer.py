import functools
from typing import Any, Callable


def get_func_call(func: Callable, args: tuple, kwargs: dict) -> str:
    """
    Formats function call information into a readable string output
    """
    output = []
    output.append(f"\n{'='*50}")
    output.append(f"[DEBUG] Function Call: {func.__name__}")
    output.append(f"{'-'*50}")

    if args:
        output.append("Positional Arguments:")
        for i, arg in enumerate(args, 1):
            output.append(
                f"  Arg {i}: {type(arg).__name__} = {
                    str(arg)[:100]}{'...' 
                                    if len(str(arg)) > 100 
                                    else ''}"
            )

    if kwargs:
        output.append("Keyword Arguments:")
        for key, value in kwargs.items():
            if key == "config_params" and hasattr(value, "__dict__"):
                output.append(f"  {key}: ContentType(config)")
                output.append(
                    f"    - Categories: {getattr(value, 'categories', 'N/A')}"
                )
                output.append(f"    - Types: {getattr(value, 'types', 'N/A')}")
                output.append(f"    - Words: {getattr(value, 'words', 'N/A')}")
            else:
                output.append(
                    f"  {key}: {type(value).__name__} = {
                        str(value)[:100]}{'...' 
                                          if len(str(value)) > 100 
                                          else ''}"
                )

    output.append(f"{'='*50}\n")
    return "\n".join(output)
