import re
from typing import Dict, List, Optional


class TextReviser:   
    def __init__(
        self,
        specific_words: Optional[Dict[str, List[str]]] = None,
        transcription_result: Optional[dict] = None
    ):
        # Handle different input formats for specific_words
        if isinstance(specific_words, str):
            self.specific_words = {"default": [specific_words]}

        elif isinstance(specific_words, list):
            self.specific_words = {"default": specific_words}

        else:
            self.specific_words = specific_words or {}
        
        # Initialize language detection
        self.detected_language = None
        if transcription_result and 'language' in transcription_result:
            print(f"Language detected: {transcription_result['language']}\n")
            self.set_detected_language(transcription_result['language'])

    def set_detected_language(self, lang_code: str):
        """Extracts and stores the base language code from Whisper's detection"""
        if lang_code and isinstance(lang_code, str):
            self.detected_language = lang_code.lower().split('-')[0]  # Convert to ISO 639-1

    def revise_text(self, text: str) -> str:
        """Main text processing pipeline"""
        if not text:
            return text

        revised_text = text
        
        # Only process technical terms if they exist
        if self.specific_words:
            revised_text = self._process_technical_terms(revised_text)

        return revised_text

    def _process_technical_terms(self, text: str) -> str:
        """Enforces consistent capitalization and formatting of technical terms"""
        for category_terms in self.specific_words:
            for term in category_terms:
                # Case-insensitive replacement with exact term
                pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
                text = pattern.sub(term, text)
                
        return text