import os
from tkinter import filedialog
from typing import Dict, List, Optional, Union, Any


from src.errors.handlers import catch_errors
from src.errors.func_printer import get_func_call
from src.errors.exceptions import ErrorCode, FileError
from src.utils.transcripting.output_debugger import OutputDebugger
from src.utils.transcripting.textify import Textify
from src.utils.pdf_exporter import PDFExporter
from src.utils.content_type import ContentType
from src.utils.text_reviser import TextReviser
from src.utils.audio_cleaner import clean_audio
from src.utils.audio_processor import extract_audio
from src.utils.file_handler import save_transcription
from src.utils.models import MODELS


class EndFlow:
    """Main transcription workflow controller"""

    model_size = str(MODELS[0])  # Default model size

    def __init__(self):
        self.transcriber = Textify(EndFlow.model_size)
        self.debugger = OutputDebugger()
        self.reviser = TextReviser()
        self.pdf_exporter = PDFExporter()
        self.content_config = ContentType(words=None, has_odd_names=True)
        # TODO: make has_odd_names dynamic

    def configure_content(
        self, config_params: Optional[Union[Dict[str, Any], ContentType]] = None
    ) -> None:
        """Configure content processing parameters"""
        if config_params is None:
            return

        if isinstance(config_params, ContentType):
            words = self._process_words(config_params.words)
            self.content_config = ContentType(
                words=words,
                types=config_params.types,
                has_code=config_params.has_code,
                has_odd_names=config_params.has_odd_names,
                is_multilingual=config_params.is_multilingual,
            )

        elif isinstance(config_params, dict):
            config_dict = dict(config_params)
            if "words" in config_dict:
                config_dict["words"] = self._process_words(config_dict["words"])

            self.content_config = ContentType(**config_dict)

        if self.content_config.words:
            self.reviser.specific_words = self.content_config.words  # type: ignore

    def _process_words(self, words: Any) -> Optional[Dict[str, List[str]]]:
        """Convert words to proper dict format if needed"""
        if isinstance(words, list):
            return {word: [] for word in words}

        return words if isinstance(words, dict) else None

    @catch_errors
    def process_video(
        self, 
        video_path: str, 
        config_params: Optional[Dict[str, Any]] = None, 
        pretty_notes: bool = False,
        **kwargs
    ) -> str:
        """Process video file through full transcription pipeline"""
        if config_params:
            self.configure_content(config_params)

        audio = extract_audio(video_path)
        cleaned = clean_audio(audio)
        prompt = self.debugger.generate_content_prompt(self.content_config)

        result = self.transcriber.transcribe(
            cleaned,
            initial_prompt=prompt,
            temperature=0.2 if self.content_config.types else 0.5,
            **kwargs,
        )

        revised_text = self.reviser.revise_text(result["text"])
        if not revised_text:
            print(
                get_func_call(
                    self.process_video,
                    (video_path,),
                    {"config_params": config_params, **kwargs},
                )
            )

        return self._save_result(
            revised_text, 
            os.path.basename(video_path),
            pretty_notes=pretty_notes
        )

    def _save_result(
    self, 
    text: str, 
    source_filename: str = "", 
    pretty_notes: bool = False
) -> str:
        """Save results with consistent error handling"""
        try:
            if not text.strip():
                raise FileError.empty_text()

            # Determine file extension and format based on pretty_notes flag
            extension = ".pdf" if pretty_notes else ".txt"
            base_name = os.path.splitext(source_filename)[0]
            default_filename = f"{base_name}_transcription{extension}"

            # Automatically generate the save path without dialog
            save_path = os.path.join(os.path.expanduser("~"), "Downloads", default_filename)
            
            # Ensure unique filename if file already exists
            counter = 1
            while os.path.exists(save_path):
                save_path = os.path.join(
                    os.path.expanduser("~"), 
                    "Downloads",
                    f"{base_name}_transcription_{counter}{extension}"
                )
                counter += 1

            if pretty_notes:
                # Save as PDF
                if not self.pdf_exporter.export_to_pdf(
                    text,
                    save_path,
                    f"Transcription: {base_name}",
                ):
                    raise FileError.pdf_creation_failed()
            else:
                # Save as TXT
                save_transcription(text, save_path)

            return save_path

        except FileError:
            raise
        except Exception as e:
            raise FileError(
                code=ErrorCode.FILE_ERROR,
                message="Unexpected save error",
                context={"error_type": type(e).__name__, "error_details": str(e)},
            ) from e