import logging
import traceback



def configure_logging():
    """Configure basic logging setup"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def log_unexpected_error(error: Exception):
    """Log unexpected errors with traceback"""
    logging.error(f"Unexpected error: {str(error)}")
    logging.debug(f"Traceback:\n{traceback.format_exc()}")