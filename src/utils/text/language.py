from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class LanguageConfig:
    """Configuration for language processing"""
    default_language: str = "portuguese"
    supported_languages: List[str] = field(
        default_factory=lambda: ["english", "portuguese", "spanish", "italian"]
    )
    fallback_patterns: str = "default"


class Language:
    """Centralized language detection and processing from Whisper output"""
    def __init__(self, config: Optional[LanguageConfig] = None):
        self.config = config or LanguageConfig()
        self.detected_language: Optional[str] = None

    def process_whisper_output(self, transcription_result: Dict[str, Any]) -> None:
        """Process Whisper's output to extract and validate language"""
        if not transcription_result or not isinstance(transcription_result, dict):
            return

        lang_code = transcription_result.get("language")
        if not lang_code or not isinstance(lang_code, str):
            return

        # Clean and extract base language code
        lang = lang_code.lower().split("-")[0]

        # Validate against supported languages
        if lang in self.config.supported_languages:
            self.detected_language = lang
        else:
            # Try matching first 2 letters (en, pt, es, etc.)
            base_code = lang[:2]
            for supported_lang in self.config.supported_languages:
                if supported_lang.startswith(base_code):
                    self.detected_language = supported_lang
                    break

    def get_language(self) -> str:
        """Get the detected language or fallback to default"""
        return self.detected_language or self.config.default_language

    def get_language_code(self) -> str:
        """Get 2-letter language code"""
        return self.get_language()[:2]

    def is_supported_language(self, lang_code: str) -> bool:
        """Check if a language code is supported"""
        lang = lang_code.lower().split("-")[0]
        return lang in self.config.supported_languages

    def get_question_words(self, question_words_map: Dict[str, List[str]]) -> List[str]:
        """Get question words for the current language"""
        lang = self.get_language()
        return question_words_map.get(
            lang, question_words_map[self.config.fallback_patterns]
        )

    def get_definition_patterns(self, patterns_map: Dict[str, List[str]]) -> List[str]:
        """Get definition patterns for the current language"""
        lang = self.get_language()
        return patterns_map.get(lang, patterns_map[self.config.fallback_patterns])
