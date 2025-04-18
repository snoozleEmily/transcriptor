from tkinter import filedialog
from typing import List, Optional


from src.errors.handlers import catch_errors
from src.errors.exceptions import ErrorCode, FileError
from src.utils.textify import Textify
from src.utils.text_reviser import TextReviser
from src.utils.file_handler import save_transcription
from src.utils.audio_cleaner import clean_audio
from src.utils.audio_processor import extract_audio

# TODO: Add specific_words to be received from the user's input in the GUI

class EndFlow:
    def __init__(self, words: Optional[List[str]] = None):
        self.textify = Textify()
        words = ["AI", "Machine Learning", "NLP"] # For testing | it will be removed
        self.reviser = TextReviser(specific_words=words)

    @catch_errors
    def process_video(self, video_path: str) -> str:
        """Process video through transcription pipeline with technical term validation"""
        audio = extract_audio(video_path)
        cleaned = clean_audio(audio)

        # Extract text from the result dictionary
        result = self.textify.transcribe(cleaned)
        raw_text = result['text']
        revised_text = self.reviser.revise_text(raw_text)

        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )

        if not save_path:
            raise FileError(
                code=ErrorCode.FILE_ERROR,
                message="Save cancelled by user"
            )

        save_transcription(revised_text, save_path)
        return save_path
