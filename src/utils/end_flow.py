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
        self, video_path: str, config_params: Optional[Dict[str, Any]] = None, **kwargs
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

        return self._save_result(revised_text, os.path.basename(video_path))

    def _save_result(self, text: str, source_filename: str = "") -> str:
        """Save results to user-selected file format"""
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("PDF Files", "*.pdf")],
            title="Save Transcription As",
            initialfile=os.path.splitext(source_filename)[0],
        )

        if not save_path:
            raise FileError(code=ErrorCode.FILE_ERROR, message="Save cancelled by user")

        try:
            if save_path.lower().endswith(".pdf"):
                success = self.pdf_exporter.export_to_pdf(
                    text,
                    save_path,
                    f"Transcription: {os.path.splitext(source_filename)[0]}",
                )
                if not success:
                    raise FileError(
                        code=ErrorCode.FILE_ERROR, message="PDF creation failed"
                    )
            else:
                save_transcription(text, save_path)

            return save_path

        except Exception as e:
            raise FileError(code=ErrorCode.FILE_ERROR, message=f"Save failed: {str(e)}")
