from tkinter import filedialog
from typing import List, Optional


from src.errors.handlers import catch_errors
from src.errors.exceptions import ErrorCode, FileError
from src.utils.transcriber import Transcriber
from src.utils.text_reviser import AdvancedTextReviser
from src.utils.file_handler import save_transcription
from src.utils.audio_cleaner import clean_audio
from src.utils.audio_processor import extract_audio


class ProcessingController:
    def __init__(self, technical_terms: Optional[List[str]] = None):
        self.transcriber = Transcriber()
        self.reviser = AdvancedTextReviser(technical_terms=technical_terms)

    @catch_errors
    def process_video(self, video_path: str) -> str:
        """Process video through transcription pipeline with technical term validation"""
        audio = extract_audio(video_path)
        cleaned = clean_audio(audio)

        raw_text = self.transcriber.transcribe(cleaned)
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
