import re
from typing import List, Dict, Any, Optional


from src.utils.text.word_snippets import QUESTION_WRD, DEFINITION_PAT
from src.errors.exceptions import FileError, TranscriptionError
from src.errors.logging import log_unexpected_error



class NotesGenerator:
    def __init__(self, language, config):
        self.language = language
        self.config = config

    def create_notes(self, data: Dict[str, Any]) -> str:
        """Minimal notes generator for pipeline testing."""
        if not data.get("text"):
            raise TranscriptionError.no_result()

        # Dummy output to verify EndFlow integration
        return f"# Notes\n- Raw text length: {len(data['text'])} chars\n- Language: {self.language.get_language()}"
