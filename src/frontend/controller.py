from tkinter import filedialog


from src.errors.handlers import catch_errors
from src.errors.exceptions import ErrorCode, FileError
from src.utils.transcriber import Transcriber
from src.utils.file_handler import save_transcription
from src.utils.audio_cleaner import clean_audio
from src.utils.audio_processor import extract_audio



class ProcessingController:
    def __init__(self):
        self.transcriber = Transcriber()

    @catch_errors
    def process_video(self, video_path: str):
        """Process video through transcription pipeline"""
        audio = extract_audio(video_path)
        cleaned = clean_audio(audio)

        text = self.transcriber.transcribe(cleaned)

        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text Files", "*.txt")]
        )

        if not save_path:
            raise FileError(code=ErrorCode.FILE_ERROR, message="Save cancelled by user")

        save_transcription(text, save_path)

        return save_path
