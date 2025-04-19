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



class EndFlow:
    models = [
        "tiny",    # 0 -> Fastest, lowest accuracy
        "base",    # 1 -> Fast, low accuracy
        "small",   # 2 -> Medium speed, medium accuracy
        "medium",  # 3 -> Medium speed, high accuracy
        "large"    # 4 -> Slowest, highest accuracy
        ]
    model_size = models[1]  # Default model size for transcription
    
    def __init__(self, words: Optional[List[str]] = None):
        words = ["AI", "Machine Learning", "NLP"] # For testing | it will be removed
        self.textify = Textify()
        self.reviser = TextReviser(specific_words=words)

    def configure_content(self, config_params: dict):
        """Update content configuration from GUI inputs"""
        self.content_config = ContentType(**config_params)
        
        # Update reviser with technical terms
        if self.content_config.tech_categories:
            self.reviser.technical_terms = self.content_config.tech_categories

    @catch_errors
    def process_video(self, video_path: str) -> str:
        """Process video with domain-aware transcription"""
        if not self.content_config:
            raise ValueError("Content configuration not set")

        audio = extract_audio(video_path)
        cleaned = clean_audio(audio)

        # Generate context-aware prompt
        initial_prompt = self.transcriber._get_content_prompt(self.content_config)
        
        # Add custom vocabulary from database
        custom_terms = self._get_domain_terms()
        full_prompt = f"{initial_prompt} | Keywords: {', '.join(custom_terms)}"

        result = self.transcriber.transcribe(
            cleaned,
            initial_prompt=full_prompt,
            temperature=0.2 if self.content_config.is_technical else 0.5,
            language="en"
        )

        revised_text = self.reviser.revise_text(result['text'])
        return self._save_result(revised_text)

    def _get_domain_terms(self) -> List[str]:
        """Retrieve domain-specific terms from database"""
        return [
            "Terraform",
            "Kubernetes",
            "CI/CD",
            "IaC"
        ] + self.content_config.tech_categories

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