import os
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
from src.utils.pdf_exporter import PDFExporter
from src.utils.models import MODELS



class EndFlow:
    """Main transcription workflow controller responsible for:
    - Audio extraction and cleaning
    - Speech-to-text transcription
    - Text revision and formatting
    - Final export in specified format

    Attributes:
        model_size: Whisper model version used for transcription
    """

    model_size = str(MODELS[2])  # Default model | it will be set to 3

    def __init__(self) -> None:
        """Initialize workflow components with default configuration"""
        # TODO: Implement dynamic has_odd_names detection

        self.transcriber = Textify(EndFlow.model_size)
        self.language = Language()
        self.reviser = TextReviser(language=self.language)
        self.content_config = ContentType(words=None, has_odd_names=True)
        self.notes_generator = NotesGenerator(language=self.language, config=self.content_config)
        self.pdf_exporter = PDFExporter()
        self.debugger = OutputDebugger()

    def configure_content(
        self, config_params: Optional[Union[Dict[str, Any], ContentType]] = None
    ) -> None:
        """Update content processing configuration parameters

        Args:
            config_params: Either a ContentType instance or dictionary containing:
                - words: Custom vocabulary mapping/list
                - types: Content categories (e.g., technical, medical)
                - has_code: Boolean flag for code presence
                - has_odd_names: Boolean flag for unusual proper nouns
                - is_multilingual: Boolean flag for multiple languages
        """
        if not config_params:
            return

        if isinstance(config_params, ContentType):
            # Directly use ContentType instance after processing words
            self.content_config = ContentType(
                words=self._process_words(config_params.words),
                types=config_params.types,
                has_code=config_params.has_code,
                has_odd_names=config_params.has_odd_names,
                is_multilingual=config_params.is_multilingual,
            )

        elif isinstance(config_params, dict):
            # Convert dictionary to ContentType with proper validation
            processed_params = dict(config_params)

            if "words" in processed_params:
                processed_params["words"] = self._process_words(
                    processed_params["words"]
                )
            self.content_config = ContentType(**processed_params)

        # Update text reviser with custom vocabulary if provided
        if self.content_config.words:
            self.reviser.specific_words = self.content_config.words  # type: ignore

    def _process_words(
        self, words: Optional[Union[List[str], Dict[str, List[str]]]]
    ) -> Optional[Dict[str, List[str]]]:
        """Normalize custom vocabulary input to expected dictionary format

        Args:
            words: Can be either:
                - List of terms (converted to {term: []})
                - Dictionary of {term: [alternatives]}
                - None (returns None)

        Returns:
            Properly formatted dictionary or None if invalid input
        """
        if isinstance(words, list):
            return {word.strip(): [] for word in words if word.strip()}

        if isinstance(words, dict):
            return words

        return None

    @catch_errors
    def process_video(
        self,
        video_path: str,
        config_params: Optional[Dict[str, Any]] = None,
        pretty_notes: bool = False,
        **kwargs,
    ) -> str:
        # Update content configuration if provided
        if config_params:
            self.configure_content(config_params)

        # Audio processing pipeline
        audio = extract_audio(video_path)
        cleaned_audio = clean_audio(audio)

        # Generate transcription context prompt
        context_prompt = self.debugger.generate_content_prompt(self.content_config)

        # Perform speech-to-text transcription
        transcription_result = self.transcriber.transcribe(
            cleaned_audio,
            initial_prompt=context_prompt,
            temperature=0.2 if self.content_config.types else 0.5,
            **kwargs,
        )

        # Process the language from Whisper output
        self.language.process_whisper_output(transcription_result)

        # Post-process transcribed text
        revised_text = self.reviser.revise_text(transcription_result["text"])
        if not revised_text.strip():
            print(
                get_func_call(
                    self.process_video,
                    (video_path,),
                    {"config_params": config_params, **kwargs},
                )
            )
            raise FileError.empty_text()

        return self._save_result(
            revised_text, os.path.basename(video_path), pretty_notes=pretty_notes
        )

    def _save_result(
        self, text: str, source_filename: str = "", pretty_notes: bool = False
    ) -> str:
        if not text.strip():
            raise FileError.empty_text()

        # Generate base filename from source
        base_name = os.path.splitext(os.path.basename(source_filename))[0]
        extension = ".pdf" if pretty_notes else ".txt"

        # Create output directory path
        output_dir = os.path.expanduser("~/Downloads")
        base_filename = f"{base_name}_transcription{extension}"

        # Handle filename conflicts
        save_path = os.path.join(output_dir, base_filename)
        conflict_num = 1

        while os.path.exists(save_path):
            new_filename = f"{base_name}_transcription_{conflict_num}{extension}"
            save_path = os.path.join(output_dir, new_filename)
            conflict_num += 1

        try:
            if pretty_notes:
                # PDF generation workflow
                doc_title = f"Transcription: {base_name}"
                print(f"Original text length: {len(text)}")
                
                # Create a dict with text for notes generator
                notes_input = {
                    "text": text,
                    "language": self.language.get_language(),
                    "segments": []  # Add empty segments if your notes generator expects them
                }
                
                notes_content = self.notes_generator.create_notes(notes_input)
                print(f"Notes content length: {len(str(notes_content))}")
                
                # Convert notes content to string for PDF export
                notes_text = "\n".join(
                    f"{section}:\n{content}\n" 
                    for section, content in notes_content.items()
                )
                
                if not self.pdf_exporter.export_to_pdf(notes_text, save_path, doc_title):
                    raise FileError.pdf_creation_failed()
            else:
                # Plain text output
                save_transcription(text, save_path)

            return os.path.abspath(save_path)

        except PermissionError as perm_err:
            raise FileError.pdf_permission_denied(save_path, perm_err) from perm_err
        
        except Exception as generic_err:
            raise FileError(
                code=ErrorCode.FILE_ERROR,
                message="Unexpected save operation failure",
                context={
                    "error_type": type(generic_err).__name__,
                    "error_details": str(generic_err),
                    "output_path": save_path,
                },
            ) from generic_err
