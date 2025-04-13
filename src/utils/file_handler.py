import os
import textwrap
import datetime
from pathlib import Path


from src.errors.exceptions import FileError



def save_transcription(text: str, save_path: str = None) -> str:
    """Save transcription text to file with fallback naming"""
    try:
        if not text.strip():
            raise ValueError("Empty transcription text")

        # Generate default filename if not provided
        if not save_path:
            save_path = os.path.join(
                os.getcwd(), # Current working directory
                f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt" # Timestamp filename
            )

        # Create parent directories if needed
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Format and save text
        wrapped = textwrap.fill(text, width=80)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(wrapped)
            
        return save_path
            
    except PermissionError as e:
        raise FileError.save_failed(f"Permission denied: {save_path}") from e
    
    except Exception as e:
        raise FileError.save_failed(str(e)) from e