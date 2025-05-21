import re
from typing import List, Dict, Tuple


from src.utils.content_type import ContentType



class NotesGenerator:
    def __init__(self, config: ContentType):
        """Initialize the notes generator with configuration settings.

        Args:
            config: ContentType configuration object containing settings
                   for note generation
        """
        self.config = config

    def create_notes(self, text: str, language: str | None = None) -> str:
        """Main method to generate structured notes from input text."""
        sentences = self._universal_sentence_split(text)

    def _universal_sentence_split(self, text: str) -> List[str]:
        """Split text into sentences using language-agnostic patterns.

        Uses common sentence terminators (.!?) followed by whitespace and uppercase
        to identify sentence boundaries. Handles basic multilingual cases.
        """
        # Split on sentence terminators followed by whitespace and uppercase letter
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-öø-ȳ]|\")", text)
        return [s.strip() for s in sentences if s.strip()]
