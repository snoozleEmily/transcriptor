import os
import nltk
from tkinter import filedialog
from typing import Callable
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


from errors.handlers import catch_errors
from errors.exceptions import ErrorCode, FileError, AppError
from utils.transcriber import Transcriber
from utils.file_handler import save_transcription
from utils.audio_cleaner import clean_audio
from utils.audio_processor import extract_audio



# Configure NLTK data path for virtual environment
NLTK_DATA_PATH = os.path.join(os.path.dirname(__file__), 'venv', 'nltk_data')
nltk.data.path.append(NLTK_DATA_PATH)

LANGUAGE = "english"
SUMMARY_SENTENCES = 5

def summarize_text(text: str, sentences: int = SUMMARY_SENTENCES) -> str:
    """Generate a summary using Sumy's LSA algorithm."""
    if not text.strip():
        raise AppError(ErrorCode.SUMMARY_ERROR, "Cannot summarize empty text")
        
    if len(text.split()) < 10:  # Minimum words check
        return "Text too short for meaningful summary"

    try:
        parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)
        summary = summarizer(parser.document, sentences)
        return "\n".join(str(sentence) for sentence in summary)
    
    except Exception as e:
        raise AppError(ErrorCode.SUMMARY_ERROR, f"Summarization failed: {str(e)}")

class ProcessingController:
    def __init__(self):
        self.transcriber = Transcriber()

    @catch_errors
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
            raise FileError(ErrorCode.FILE_ERROR, "Save cancelled by user")
        
        save_transcription(text, save_path)

        progress_cb(97, "Generating summary...")
        summary = summarize_text(text)
        summary_path = self._generate_summary_path(save_path)
        save_transcription(summary, summary_path)

        progress_cb(100, "Completed!")
        
        return save_path, summary_path

    def _generate_summary_path(self, original_path: str) -> str:
        """Generate a summary file path (e.g., transcript_summary.txt)."""
        base, ext = os.path.splitext(original_path)
        
        return f"{base}_summary{ext}"