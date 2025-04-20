from tkinter import filedialog
from typing import List, Optional


from src.errors.handlers import catch_errors
from src.errors.exceptions import ErrorCode, FileError
from src.utils.textify import Textify
from src.utils.content_type import ContentType
from src.utils.text_reviser import TextReviser
from src.utils.file_handler import save_transcription
from src.utils.audio_cleaner import clean_audio
from src.utils.audio_processor import extract_audio

# TODO: Add words to be received from the user's input in the GUI

class EndFlow:
    models = [
        "tiny",    # 0 -> Fastest, lowest accuracy
        "base",    # 1 -> Fast, low accuracy
        "small",   # 2 -> Medium speed, medium accuracy
        "medium",  # 3 -> Medium speed, high accuracy
        "large"    # 4 -> Slowest, highest accuracy
        ]
    model_size = models[1]  # Default model size for transcription
    
    def __init__(self):
        self.transcriber = Textify(EndFlow.model_size)  
        self.reviser = TextReviser()
        self.content_config = ContentType(
            words=["Maha", "Zoldyck"],
            has_odd_names=True
        )

    def configure_content(self, config_params: dict):
        """Update content configuration from GUI inputs"""
        self.content_config = ContentType(**config_params)
            
        # Update reviser with technical terms
        if self.content_config.words:
            self.reviser.specific_words = self.content_config.words

    @catch_errors
    def process_video(self, video_path: str) -> str:
        """Process video with domain-aware transcription"""
        audio = extract_audio(video_path)
        cleaned = clean_audio(audio)

        # Generate context-aware prompt
        initial_prompt = self.transcriber._get_content_prompt(self.content_config)
        
        if not self.content_config:
            print("Content configuration not set\n Using default settings...")
        else:
            # Add custom vocabulary from database
            custom_terms = self._get_domain_terms()
            full_prompt = f"{initial_prompt} | Keywords: {', '.join(custom_terms)}"

        result = self.transcriber.transcribe(
            cleaned,
            initial_prompt=full_prompt,
            temperature=0.2 if self.content_config.types else 0.5,
            language="en"
        )

        revised_text = self.reviser.revise_text(result['text'])
        return self._save_result(revised_text)

    def _get_domain_terms(self) -> List[str]:
        """Retrieve domain-specific terms from database"""
        if self.content_config.words:
            return [
                "Terraform",
                "Kubernetes",
                "CI/CD",
                "IaC"
            ] + self.content_config.words

    def _save_result(self, text: str) -> str:
        """Handle file saving with error checking"""
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )
        if not save_path:
            raise FileError(
                code=ErrorCode.FILE_ERROR,
                message="Save cancelled by user"
            )
        save_transcription(text, save_path)
        return save_path