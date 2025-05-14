import os
from tkinter import filedialog


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
    model_size = MODELS[1]  # Default model size

    def __init__(self):
        self.transcriber = Textify(EndFlow.model_size)
        self.debugger = OutputDebugger()
        self.reviser = TextReviser()
        self.pdf_exporter = PDFExporter()
        self.content_config = ContentType(words=[], has_odd_names=True)

    def configure_content(self, config_params):
        """Update content configuration handling both dict and ContentType"""
        if config_params is None:
            return
            
        if isinstance(config_params, ContentType):
            # If already a ContentType, just copy the relevant attributes
            self.content_config = ContentType(
            words=config_params.words,
            types=config_params.types,
            has_code=config_params.has_code,
            has_odd_names=config_params.has_odd_names,
            is_multilingual=config_params.is_multilingual
        )
        elif isinstance(config_params, dict):
            # If it's a dictionary, unpack it
            self.content_config = ContentType(**config_params)
        else:
            raise ValueError("config_params must be either a dict or ContentType")

        if self.content_config.words:
            self.reviser.specific_words = self.content_config.words

    @catch_errors
    def process_video(self, video_path: str, config_params: dict = None, **kwargs):
        """Process video with optional progress callback"""
        if config_params:
            self.configure_content(config_params)

        audio = extract_audio(video_path)
        cleaned = clean_audio(audio)
        prompt = self.debugger.generate_content_prompt(self.content_config)

        result = self.transcriber.transcribe(
            cleaned,
            initial_prompt=prompt,
            temperature=0.2 if self.content_config.types else 0.5,
            **kwargs  # Pass through any additional kwargs
        )

        revised_text = self.reviser.revise_text(result["text"])

        if not revised_text:
            print(get_func_call(
            self.process_video,
                (video_path,),
                {"config_params": config_params, **kwargs}
            ))

        return self._save_result(revised_text)    

    def _save_result(self, text: str, source_filename: str = "") -> str:
        """Handle file saving with both TXT and PDF options"""
        # First save as TXT
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("PDF Files", "*.pdf")],
            title="Save Transcription As",
            initialfile=os.path.splitext(source_filename)[0]
        )
        
        if not save_path:
            # TODO: Add saving transcription automatically in the .exe location
            raise FileError(
                code=ErrorCode.FILE_ERROR,
                message="Save cancelled by user"
            )
        try:
            if save_path.lower().endswith('.pdf'):
                print("\nExporting to PDF...")
                success = self.pdf_exporter.export_to_pdf(
                    text,
                    save_path,
                    title=f"Transcription: {os.path.splitext(source_filename)[0]}"
                )
                print(f"PDF export success: {success}")
                if not success:
                    raise FileError(
                        code=ErrorCode.FILE_ERROR,
                        message="Failed to save PDF file"
                    )
            else:
                print("\nSaving as TXT...")
                save_transcription(text, save_path)
                
            return save_path
        
        except Exception as e:
            raise FileError(
                code=ErrorCode.FILE_ERROR,
                message=f"Error when saving the result: {str(e)}"
            )
        