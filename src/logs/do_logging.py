import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"


def configure_logging(
    log_level: int = logging.INFO,
    log_file: Optional[Path] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> None:
    """
    Configure centralized logging with console + optional rotating file handler.
    Safe to call once at application startup.
    """
    import sys

    handlers = []

    # console handler
    console = logging.StreamHandler(sys.stdout)
    handlers.append(console)

    # optional rotating file handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_h = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        handlers.append(file_h)

    formatter = logging.Formatter(fmt=DEFAULT_FORMAT, datefmt=DATEFMT)
    for h in handlers:
        h.setFormatter(formatter)

    # Configure root logger
    root = logging.getLogger()
    root.setLevel(log_level)

    # Remove existing handlers to avoid duplicates if reconfiguring in tests
    for h in list(root.handlers):
        root.removeHandler(h)

    for h in handlers:
        root.addHandler(h)


def log_unexpected_error(exc_type, exc_value, exc_traceback) -> None:
    """
    Log unexpected exceptions; designed to be used as sys.excepthook or threading.excepthook.
    Accepts the standard excepthook signature.
    """
    logger = logging.getLogger("app.uncaught")
    logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


def install_global_exception_hooks() -> None:
    """
    Install hooks so uncaught exceptions from main thread and other threads are logged.
    Call this after configure_logging().
    """
    import sys, threading

    def _sys_hook(exc_type, exc_value, exc_tb):
        log_unexpected_error(exc_type, exc_value, exc_tb)

    sys.excepthook = _sys_hook

    def _thread_hook(args):
        log_unexpected_error(args.exc_type, args.exc_value, args.exc_traceback)

    try:
        threading.excepthook = _thread_hook

    except Exception:
        # older Pythons: we can't set threading.excepthook, but we attempted
        pass
