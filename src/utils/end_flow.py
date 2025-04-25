from tkinter import filedialog
from typing import List


from src.errors.handlers import catch_errors
from src.errors.exceptions import ErrorCode, FileError
from src.utils.transcripting.textify import Textify
from src.utils.models import MODELS
from src.utils.content_type import ContentType
from src.utils.text_reviser import TextReviser
from src.utils.file_handler import save_transcription
from src.utils.audio_cleaner import clean_audio
from src.utils.audio_processor import extract_audio
from src.utils.transcripting.output_debugger import OutputDebugger


# TODO: Add words to be received from the user's input in the GUI


class EndFlow:
    model_size = MODELS[2]  # Default model size for transcription
    # TODO: Add a way to set the model size from the GUI

    def __init__(self):
        self.transcriber = Textify(EndFlow.model_size)
        self.debugger = OutputDebugger()
        self.reviser = TextReviser()
        self.content_config = ContentType(words=["Maha", "Zoldyck"], has_odd_names=True)

    def configure_content(self, config_params: dict):
        """Update content configuration from GUI inputs"""
        self.content_config = ContentType(**config_params)

        # Update reviser with technical terms
        if self.content_config.words:
            self.reviser.specific_words = self.content_config.words

    @catch_errors
    def process_video(self, video_path: str) -> str:
        audio = extract_audio(video_path)
        cleaned = clean_audio(audio)

        # Generate prompt using the debugger
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
        )

        revised_text = self.reviser.revise_text(result["text"])
        return self._save_result(revised_text)

    def _get_domain_terms(self) -> List[str]:
        """Retrieve domain-specific terms from database"""
        if self.content_config.words:
            return [
                "Terraform",
                "Kubernetes",
                "CI/CD",
                "IaC",
            ] + self.content_config.words

    def _save_result(self, text: str) -> str:
        """Handle file saving with error checking"""
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text Files", "*.txt")]
        )
        if not save_path:
            raise FileError(code=ErrorCode.FILE_ERROR, message="Save cancelled by user")
        
        save_transcription(text, save_path)
        return save_path
