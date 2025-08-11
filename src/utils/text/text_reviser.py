import re
from typing import Dict, List, Optional, Tuple


from src.errors import LanguageError
from src.utils.text.language import Language
from src.utils.text.words.question import QUESTION_WRD 
from src.utils.text.words.definition_pat import DEFINITION_PAT



class TextReviser:
    def __init__(
        self,
        language: Language,
        odd_words: Optional[Dict[str, List[str]]] = None,
    ):
        self.language_processor = language

        # Normalize specific_words into a dict-of-lists
        if isinstance(odd_words, str):
            self.specific_words = {"default": [odd_words]}

        elif isinstance(odd_words, list):
            self.specific_words = {"default": odd_words}

        else:
            self.specific_words = odd_words or {}

    def _split_with_timestamps(
        self, text: str
    ) -> List[Tuple[str, Optional[float]]]:
        """Split text into sentences; return (sentence, None)."""
        try:
            sentences = re.split(r"(?<=[.!?])\s+", text)

        except Exception as e:
            raise LanguageError.sentence_split_failed(e)

        return [(sent, None) for sent in sentences if sent.strip()]

    def _detect_questions(self, text: str) -> List[Tuple[str, Optional[float]]]:
        """
        Find interrogative sentences by checking if the first word
        appears in the language's question-words list.
        """
        question_words = set(self.language_processor.get_question_words(QUESTION_WRD))
        questions: List[Tuple[str, Optional[float]]] = []

        for sent, start_time in self._split_with_timestamps(text):
            tokens = sent.split()
            if tokens:
                first_word = tokens[0].lower()

                if first_word in question_words:
                    questions.append((sent, start_time))

        return questions

    def _find_definitions(self, text: str) -> List[str]:
        """Extract definitions using language-specific regex patterns."""
        patterns = self.language_processor.get_definition_patterns(DEFINITION_PAT)
        definitions: List[str] = []
        
        for pattern in patterns:
            definitions.extend(re.findall(pattern, text))

        return definitions

    def _process_technical_terms(self, text: str) -> str:
        """
        Enforce consistent capitalization/formatting of any terms
        provided in specific_words.
        """
        if not self.specific_words:
            return text

        for category_terms in self.specific_words.values():
            for term in category_terms:
                pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
                text = pattern.sub(term, text)

        return text

    def revise_text(self, text: str) -> str:
        """Main pipeline: apply technical-term formatting (if any)."""
        if not text:
            return text

        revised_text = text
        if self.specific_words:
            revised_text = self._process_technical_terms(revised_text)

        return revised_text
