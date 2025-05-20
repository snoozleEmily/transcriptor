import os
import textwrap
from pathlib import Path
from typing import Optional
from datetime import datetime


from src.errors.exceptions import FileError



def save_transcription(text: str, save_path: Optional[str] = None) -> str:
    """Saves transcribed text to a file, with automatic naming if path not provided.
    
    Args:
        text: The transcribed text to save
        save_path: Optional path for the output file. If None, generates a timestamped filename.
    
    Returns:
        Path where the file was saved
    
    Raises:
        FileError: If text is empty or file cannot be written
    """
    try:
        # Validate we have content to save
        if not text.strip():
            raise FileError.empty_text("Transcription text cannot be empty")

        # Generate default filename using current timestamp if no path provided
        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = os.path.join(os.getcwd(), f"transcription_{timestamp}.txt")

        # Ensure parent directories exist
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        # Save with text wrapping at 80 characters
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(textwrap.fill(text, width=80))

        return save_path

    except PermissionError as err:
        raise FileError.save_failed(error=err) from err
    
    except Exception as err:
        raise FileError.save_failed(error=err) from err