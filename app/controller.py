from tkinter import filedialog
from typing import Callable

from errors.handlers import error_handler
from errors.exceptions import ErrorCode, FileError, AppError
from utils import Transcriber, extract_audio, clean_audio, save_transcription


class ProcessingController:
    def __init__(self):
        self.transcriber = Transcriber()

    @error_handler
    def process_video(self, video_path: str, progress_cb: Callable[[int, str], None]):
        """Process video through transcription pipeline"""
        progress_cb(10, "Extracting audio...")
        audio = extract_audio(video_path)

        progress_cb(30, "Cleaning audio...")
        cleaned = clean_audio(audio)

        progress_cb(50, "Transcribing...")
        text = self.transcriber.transcribe(
            cleaned,
            lambda p: progress_cb(50 + int(p * 0.4), f"Transcribing ({int(p)}%)"),
        )

        progress_cb(95, "Saving...")
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text Files", "*.txt")]
        )

        if not save_path:
            raise FileError(code=ErrorCode.FILE_ERROR, message="Save cancelled by user")

        save_transcription(text, save_path)
        progress_cb(100, "Completed!")
        return save_path
