import textwrap

from errors.exceptions import FileError



def save_transcription(text: str, path: str) -> None:
    """Save formatted transcription"""
    try:
        wrapped = textwrap.fill(text, width=80)
        with open(path, "w", encoding="utf-8") as f:
            f.write(wrapped)

    except Exception as e:
        raise FileError.save_failed(e)