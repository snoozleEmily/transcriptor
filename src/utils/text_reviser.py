import re
from typing import Dict, List, Optional



class TextReviser:   
    def __init__(
        self,
        specific_words: Optional[Dict[str, List[str]]] = None,
        script_result: Optional[dict] = None
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
        if script_result and 'language' in script_result:
            print(f"Language detected: {script_result['language']}\n")
            self.set_detected_language(script_result['language'])

    def set_detected_language(self, lang_code: str):
        """Extracts and stores the base language code from Whisper's detection"""
        if lang_code and isinstance(lang_code, str):
            self.detected_language = lang_code.lower().split('-')[0]  # Convert to ISO 639-1

    def get_language(self) -> str: # Is it possible to avoid default lang?
        """Return detected language or default 'english'."""
        return self.detected_language if self.detected_language else "portuguese"
    
    def _detect_questions(self, text: str) -> list:
        """Find interrogative sentences using TextBlob"""
        from textblob import TextBlob
        return [
            (sent, start_time) 
            for sent, start_time in self._split_with_timestamps(text)
            if TextBlob(sent).tags[0][1] == 'WP'  # Who/What/Why
        ]

    def _find_definitions(self, text: str) -> list:
        """Regex-based definition extraction"""
        definition_pattern = r"(\b[A-Z][a-z]+\b) (is|are) (.+?)(?=[\.\n])"
        return re.findall(definition_pattern, text)
    
    def _process_technical_terms(self, text: str) -> str:
        """Enforces consistent capitalization and formatting of technical terms"""
        for category_terms in self.specific_words:
            for term in category_terms:
                # Case-insensitive replacement with exact term
                pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
                text = pattern.sub(term, text)
                
        return text

    def revise_text(self, text: str) -> str:
        """Main text processing pipeline"""
        if not text:
            return text

        revised_text = text
        
        # Only process technical terms if they exist
        if self.specific_words:
            revised_text = self._process_technical_terms(revised_text)

        return revised_text

    