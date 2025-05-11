import os
from tkinter import filedialog
from typing import List, Tuple, Optional, Callable


from src.errors.handlers import catch_errors
from src.errors.exceptions import ErrorCode, FileError
from src.utils.transcripting.output_debugger import OutputDebugger
from src.utils.transcripting.textify import Textify
from src.utils.audio_cleaner import clean_audio
from src.utils.audio_processor import extract_audio
from src.utils.file_handler import save_transcription
from src.utils.content_type import ContentType
from src.utils.text_reviser import TextReviser
from src.utils.notes_generator import NotesGenerator
from src.utils.pdf_exporter import PDFExporter
from src.utils.models import MODELS


class EndFlow:
    model_size = MODELS[2]  # Default model size for transcription

    def __init__(self):
        self.transcriber = Textify(EndFlow.model_size)
        self.debugger = OutputDebugger()
        self.reviser = TextReviser()
        self.notes_gen = None  # Will be initialized in configure_content
        self.content_config = ContentType(words=[], has_odd_names=True)

    def configure_content(self, config_params: dict):
        """Update content configuration from GUI inputs."""
        self.content_config = ContentType(**config_params)
        self.notes_gen = NotesGenerator(self.content_config)

        # Update reviser with technical terms
        if self.content_config.words:
            self.reviser.specific_words = self.content_config.words

    @catch_errors
    def process_video(
        self,
        video_path: str,
        config_params: dict = None,
        progress_callback: Optional[Callable] = None,
    ) -> Tuple[str, Optional[str]]:
        """
        Process video and return tuple of (transcript_path, notes_path).

        Args:
            video_path: Path to input video file
            config_params: Optional content configuration parameters

        Returns:
            Tuple containing paths to saved transcript and notes PDF
        """
        # Update content configuration if parameters are provided
        if config_params:
            self.content_config = config_params
            self.notes_gen = NotesGenerator(self.content_config)
            self.reviser.specific_words = self.content_config.words

        # 1. Extract and clean audio
        audio = extract_audio(video_path)
        cleaned = clean_audio(audio)

        # 2. Generate transcription
        prompt = self.debugger.generate_content_prompt(self.content_config)
        custom_terms = self._get_domain_terms()
        full_prompt = (
            f"{prompt} | Keywords: {', '.join(custom_terms)}"
            if custom_terms
            else prompt
        )

        result = self.transcriber.transcribe(
            cleaned,
            initial_prompt=full_prompt,
            temperature=0.2 if self.content_config.types else 0.5,
            progress_handler=progress_callback,
        )

        # 3. Revise and save transcript
        revised_text = self.reviser.revise_text(result["text"])
        transcript_path = self._save_transcript(revised_text)

        # Generate and save notes
        notes_path = None
        if self.notes_gen:
            notes, _ = self.notes_gen.create_notes(revised_text)
            notes_path = self._save_notes(notes, os.path.splitext(transcript_path)[0])

        return transcript_path, notes_path

    def _save_transcript(self, text: str) -> str:
        """Save revised transcript to text file."""
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save Transcript As",
        )
        if not save_path:
            raise FileError(
                code=ErrorCode.FILE_ERROR, message="Transcript save cancelled"
            )

        save_transcription(text, save_path)
        return save_path

    def _save_notes(self, notes: str, base_path: str) -> Optional[str]:
        """Save generated notes to PDF."""
        notes_path = f"{base_path}_notes.pdf"

        if PDFExporter.export_to_pdf(notes, notes_path, "Notes"):
            return notes_path

        return None

    def _get_domain_terms(self) -> List[str]:
        """Retrieve domain-specific terms from configuration."""
        custom_terms = ["Terraform", "Kubernetes", "CI/CD", "IaC"]

        # Get words from content config
        content_words = self.content_config.words

        # Handle case where words is a single string
        if isinstance(content_words, str):
            content_words = [content_words]  # Convert to list

        # Merge terms only if we have valid words
        if content_words and isinstance(content_words, list):
            return custom_terms + content_words

        return custom_terms  # Return default terms if no valid words
