import os
from tkinter import filedialog
from typing import Dict, List, Optional, Union, Any


from src.errors.handlers import catch_errors
from src.errors.func_printer import get_func_call
from src.errors.exceptions import ErrorCode, FileError
from src.utils.text.language import Language
from src.utils.text.content_type import ContentType
from src.utils.text.text_reviser import TextReviser
from src.utils.text.notes_generator import NotesGenerator
from src.utils.transcripting.output_debugger import OutputDebugger
from src.utils.transcripting.textify import Textify
from src.utils.audio_cleaner import clean_audio
from src.utils.audio_processor import extract_audio
from src.utils.file_handler import save_transcription
from src.utils.pdf_maker import PDFExporter
from src.utils.models import MODELS


class EndFlow:
    """Pipeline: audio → text → PDF"""

    model_size = str(MODELS[1])  # Default model

    def __init__(self) -> None:
        """Initialize with dependency injection-ready components."""
        self.transcriber = Textify(EndFlow.model_size)
        self.language = Language()
        self.reviser = TextReviser(language=self.language)
        self.content_config = ContentType(words=None, has_odd_names=True)
        self.pdf_exporter = PDFExporter()
        self.debugger = OutputDebugger()
        self.notes_generator = NotesGenerator(
            language=self.language, config=self.content_config
        )

    # -------------------- Content Configuration ---------------------
    def configure_content(
        self, config_params: Optional[Union[Dict[str, Any], ContentType]] = None
    ) -> None:
        """Enhanced content configuration with validation."""
        if not config_params:
            return

        try:
            if isinstance(config_params, ContentType):
                self.content_config = self._process_content_type(config_params)

            else:
                self.content_config = self._process_config_dict(config_params)

            self._update_dependencies()

        except Exception as e:
            raise FileError(
                code=ErrorCode.UNEXPECTED_ERROR,
                message="Invalid content configuration",
                context={"error_details": str(e)},
            )

    def _process_content_type(self, config: ContentType) -> ContentType:
        """Process ContentType instance with word normalization."""
        return ContentType(
            words=self._normalize_words(config.words),
            types=config.types,
            has_code=config.has_code,
            has_odd_names=config.has_odd_names,
            is_multilingual=config.is_multilingual,
        )

    def _process_config_dict(self, config: Dict[str, Any]) -> ContentType:
        """Process dictionary config with validation."""
        processed = config.copy()
        if "words" in processed:
            processed["words"] = self._normalize_words(processed["words"])

        return ContentType(**processed)

    def _normalize_words(
        self, words: Optional[Union[List[str], Dict[str, List[str]]]]
    ) -> Optional[Dict[str, List[str]]]:
        """Standardize word input format with cleaning."""
        if not words:
            return None

        if isinstance(words, list):
            return {w.strip(): [] for w in words if w.strip()}

        return words

    def _update_dependencies(self) -> None:
        """Update dependent components with new config."""
        if self.content_config.words and isinstance(self.content_config.words, dict):
            self.reviser.odd_words = self.content_config.words

        self.notes_generator.config = self.content_config

    # ----------------------- Core Processing -----------------------
    @catch_errors
    def process_video(
        self,
        video_path: str,
        config_params: Optional[Dict[str, Any]] = None,
        quick_script: bool = False,
        **kwargs,
    ) -> str:
        """Enhanced transcription pipeline with better error context."""
        self.configure_content(config_params)

        try:
            # Audio processing
            audio = extract_audio(video_path)
            cleaned_audio = clean_audio(audio)

            # Transcription
            context_prompt = self.debugger.generate_content_prompt(self.content_config)
            result = self._transcribe_audio(cleaned_audio, context_prompt, **kwargs)

            # Post-processing
            revised_text = self.reviser.revise_text(result["text"])
            if not revised_text.strip():
                raise FileError.empty_text()

            return self._save_output(
                result, revised_text, os.path.basename(video_path), quick_script
            )
        except Exception as e:
            self._log_error_context(video_path, config_params, kwargs)
            raise

    def _transcribe_audio(
        self, audio: Any, context_prompt: str, **kwargs
    ) -> Dict[str, Any]:
        """Execute transcription with proper error context."""
        return self.transcriber.transcribe(
            audio,
            initial_prompt=context_prompt,
            temperature=0.2 if self.content_config.types else 0.5,
            **kwargs,
        )

    # ----------------------- Output Handling -----------------------
    def _save_output(
        self,
        result: Dict[str, Any],
        revised_text: str,
        source_name: str,
        quick_script: bool,
    ) -> str:
        """Handle output saving with validation."""
        save_path = self._get_save_path(
            os.path.splitext(source_name)[0], ".txt" if quick_script else ".pdf"
        )
        print(f"The flag quick_script is set to: {quick_script}")
        if not quick_script:
            self.pdf_exporter.save_notes(
                result,
                revised_text,
                save_path,
                self.reviser.odd_words if hasattr(self.reviser, "odd_words") else {},
                language=self.language,
                config=self.content_config,
            )
        else:
            save_transcription(revised_text, save_path)

        return os.path.abspath(save_path)

    # ----------------------- File Management ----------------------
    def _get_save_path(self, base_name: str, extension: str) -> str:
        """Improved path handling with better fallbacks."""
        try:
            file_types = (
                [("PDF Files", "*.pdf")]
                if extension == ".pdf"
                else [("Text Files", "*.txt")]
            )
            initial_file = f"{base_name}_transcription{extension}"

            if path := filedialog.asksaveasfilename(
                title="Save transcription",
                defaultextension=extension,
                initialfile=initial_file,
                filetypes=file_types,
            ):
                return path
            
        except Exception:
            pass

        return self._generate_desktop_path(base_name, extension)

    def _generate_desktop_path(self, base_name: str, extension: str) -> str:
        """Generate numbered fallback paths on desktop."""
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        counter = 1
        path = os.path.join(desktop, f"{base_name}_transcription{extension}")

        while os.path.exists(path):
            path = os.path.join(
                desktop, f"{base_name}_transcription_{counter}{extension}"
            )
            counter += 1

        return path

    # -------------------------- Debugging -------------------------
    def _log_error_context(
        self,
        video_path: str,
        config_params: Optional[Dict[str, Any]],
        kwargs: Dict[str, Any],
    ) -> None:
        """Log detailed error context for debugging."""
        config_dict = {} if config_params is None else config_params
        print(
            get_func_call(
                self.process_video,
                (video_path,),
                {"config_params": config_dict, **kwargs},
            )
        )
