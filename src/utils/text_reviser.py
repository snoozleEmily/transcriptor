import re
from typing import Dict, List, Optional
from dataclasses import dataclass



@dataclass
class LanguageRule:
    quotation_pairs: Dict[str, str]
    special_cases: Dict[str, str] 

class TextReviser:
    # Default language rules (could be moved to config/json)
    LANGUAGE_RULES = { 
        'fr': LanguageRule(
            quotation_pairs={'« ': ' »'},
            special_cases={}
        ),
        'de': LanguageRule(
            quotation_pairs={'„': '“'},
            special_cases={}
        ),
        # Add more languages?
    }
    
    def __init__(
        self,
        specific_words: Optional[Dict[str, List[str]]] = None,
        language_rules: Optional[Dict[str, LanguageRule]] = None
    ):
        # Convert string input to dictionary format
        if isinstance(specific_words, str):
            self.specific_words = {"default": [specific_words]}
        elif isinstance(specific_words, list):
            self.specific_words = {"default": specific_words}
        else:
            self.specific_words = specific_words or {}
        
        self.language_rules = language_rules or self.LANGUAGE_RULES
        self.detected_language = None

    def set_detected_language(self, lang_code: str):
        """Validates and sets the language code"""
        if lang_code:
            self.detected_language = lang_code.lower().split('-')[0]

    def revise_text(self, text: str) -> str:
        """Main revision pipeline"""
        if not text:
            return text

        revised_text = text
        
        # Language processing if detected
        if self.detected_language:
            revised_text = self._apply_language_rules(revised_text)

        # Technical term processing
        if self.specific_words:
            revised_text = self._process_technical_terms(revised_text)

        return revised_text

    def _apply_language_rules(self, text: str) -> str:
        """Applies language-specific formatting rules"""
        if self.detected_language not in self.language_rules:
            return text

        rules = self.language_rules[self.detected_language]
        text = self._process_quotations(text, rules.quotation_pairs)
        text = self._process_special_cases(text, rules.special_cases)

        return text

    def _process_quotations(self, text: str, quotation_pairs: Dict[str, str]) -> str:
        """Replace generic quotes with language-specific ones"""
        for open_q, close_q in quotation_pairs.items():
            parts = text.split('"')

            # Only process if we have an even number of quotes
            if len(parts) > 1 and len(parts) % 2 == 1:
                text = ''
                for i, part in enumerate(parts):
                    if i == 0:
                        text += part

                    elif i % 2 == 1:
                        text += open_q + part

                    else:
                        text += close_q + part

        return text

    def _process_special_cases(self, text: str, special_cases: Dict[str, str]) -> str:
        """Handle other language-specific replacements"""
        for pattern, replacement in special_cases.items():
            text = text.replace(pattern, replacement)

        return text

    def _process_technical_terms(self, text: str) -> str:
        """Enforce consistent technical term usage"""
        for category, terms in self.specific_words.items():
            for term in terms:
                pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
                text = pattern.sub(term, text)

        return text