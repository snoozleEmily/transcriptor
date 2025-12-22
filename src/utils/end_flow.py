import os
from typing import Dict, List, Optional, Union, Any


from src.logs.debug import debug
from src.utils.text.content_type import ContentType
from src.utils.text.language import language
from src.utils.models import WHISPER_MODELS



class EndFlow:
    """Pipeline: audio → text → PDF"""

    model_size = WHISPER_MODELS["small"]["name"]

    def __init__(self) -> None:
        """Initialize with dependency injection-ready components."""
        # Clear states
        self.transcriber = None
        self.sanitized = None

        self.language = language
        self.content_config = ContentType(words=None, has_odd_names=True)

        self.model_sz = EndFlow.model_size

        debug.dprint(
            f"EndFlow initialized | Model size={EndFlow.model_size} | Language={self.language}"
        )

    # -------------------- Content Configuration ---------------------
    def configure_content(
        self, config_params: Optional[Union[Dict[str, Any], ContentType]] = None
    ) -> None:
        """Content configuration with validation."""
        if not config_params:
            debug.dprint(
            f"config_params is empty, type: {config_params}"
        )
            return

        try:
            if isinstance(config_params, ContentType):
                self.content_config = self._process_content_type(config_params)

            else:
                self.content_config = self._process_config_dict(config_params)

            self._update_dependencies()
            debug.dprint(
                f"Content configuration updated: {self.content_config}"
            )

        except Exception as e:
            from src.logs.exceptions import ErrorCode, FileError

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
        from src.utils.text.text_reviser import TextReviser

        self.reviser = TextReviser(language=self.language)

        if self.content_config.words and isinstance(self.content_config.words, dict):
            self.reviser.odd_words = self.content_config.words
            

    # ----------------------- Core Processing -----------------------
    def process_video(
        self,
        video_path: str,
        config_params: Optional[Dict[str, Any]] = None,
        quick_script: bool = False,
        **kwargs,
    ) -> str:
        """Transcription pipeline with error context."""

        from src.utils.audio_processor import extract_audio
        from src.utils.audio_cleaner import clean_audio
        from src.utils.transcripting.sanitize_prompt import SanitizePrompt

        if not config_params and not hasattr(self, "reviser"):
            self._update_dependencies()

        self.sanitized = SanitizePrompt()
        self.configure_content(config_params)

        debug.dprint(
            f"Starting process_video: path={video_path}\n"
            f"quick_script={quick_script}\n"
            f"config={config_params}\n"
        )

        try:
            from src.utils.transcripting.transcribe_audio import transcribe_audio

            # Audio processing
            audio = extract_audio(video_path)
            debug.dprint(f"Audio extracted: length={len(audio) if audio else 0}")

            cleaned_audio = clean_audio(audio)
            debug.dprint(
                f"Audio cleaned: length={len(cleaned_audio) if cleaned_audio else 0}"
            )

            # Transcription
            context_prompt = self.sanitized.generate_content_prompt(self.content_config)
            result = transcribe_audio(
                cleaned_audio,
                context_prompt,
                self.transcriber,
                self.model_sz,
                self.content_config,
                **kwargs,
            )

            # Update language detection
            self.language.process_whisper_output(result)

            # Post-processing
            revised_text = self.reviser.revise_text(result["text"])
            if not revised_text.strip():
                from src.logs.exceptions import FileError

                raise FileError.empty_text()

            return self._save_output(
                result, revised_text, os.path.basename(video_path), quick_script
            )
        except Exception as e:
            from src.logs.func_printer import _log_error_flow_context

            _log_error_flow_context(
                self.process_video, video_path, config_params, e, kwargs
            )
            raise

    # ----------------------- Output Handling -----------------------
    def _save_output(
        self,
        result: Dict[str, Any],
        revised_text: str,
        source_name: str,
        quick_script: bool,
    ) -> str:
        """Handles output saving with validation and debug logs."""

        from src.utils.pdf_maker import PDFExporter
        from src.utils.file_handler import save_transcription

        self.pdf_exporter = PDFExporter()

        debug.dprint(f"quick_script received in EndFlow: {quick_script}")

        if quick_script:
            # For TXT, ask save path immediately
            save_path = self._get_save_path(os.path.splitext(source_name)[0], ".txt")
            debug.dprint(f"Final save path determined for TXT: {save_path}")

            if not os.access(os.path.dirname(save_path) or ".", os.W_OK):
                debug.dprint("No write permissions for the directory of the save path.")

            debug.dprint("Attempting to save as TXT...")
            save_transcription(revised_text, save_path)

            debug.dprint(
                f"TXT save operation complete. Verifying file exists: {os.path.exists(save_path)}"
            )
            print("\n✏️ Results Ready! ✏️\n")
            return os.path.abspath(save_path)

        # For PDF, first generate to a temporary path
        temp_path = os.path.join(os.path.expanduser("~"), "Desktop", "temp_output.pdf")
        debug.dprint(f"Generating PDF temporarily at: {temp_path}")

        self.pdf_exporter.save_notes(
            result,
            revised_text,
            temp_path,
            self.reviser.odd_words if hasattr(self.reviser, "odd_words") else {},
            language=self.language,
            config=self.content_config,
        )

        debug.dprint("PDF generation complete. Prompting user for save location...")
        save_path = self._get_save_path(os.path.splitext(source_name)[0], ".pdf")
        debug.dprint(f"Final save path chosen by user: {save_path}")

        if not os.access(os.path.dirname(save_path) or ".", os.W_OK):
            debug.dprint("No write permissions for the directory of the save path.")

        # Move temp PDF to user-selected path
        os.replace(temp_path, save_path)
        debug.dprint(
            f"PDF save operation complete. Verifying file exists: {os.path.exists(save_path)}"
        )
        print("\n✏️ Results Ready! ✏️\n")
        return os.path.abspath(save_path)

    # ----------------------- File Management ----------------------
    def _get_save_path(self, base_name: str, extension: str) -> str:
        """Improved path handling with better fallbacks."""
        try:
            from tkinter import filedialog
            
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

        except Exception as e:
            debug.dprint(
                f"Failed to open save dialog: {e}. Falling back to desktop path."
            )
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
