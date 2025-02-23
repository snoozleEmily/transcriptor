import logging
import sys
from pathlib import Path
from typing import Optional


def configure_logging(
    log_level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> None:
    """Configure centralized logging with rotation"""
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(
            logging.FileHandler(
                filename=log_file,
                encoding='utf-8'
            )
        )

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )

def log_unexpected_error(error: Exception) -> None:
    """Log unexpected exceptions with full context"""
    logging.error(
        "Unexpected error occurred: %s",
        str(error),
        exc_info=True
    )