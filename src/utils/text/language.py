from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field


from src.errors.debug import debug


@dataclass
class LanguageConfig:
    """Configuration for language processing"""
    default_language: str = "portuguese"
    supported_languages: List[str] = field(
        default_factory=lambda: ["english", "portuguese", "spanish", "italian", "romanian"]
    )
    fallback_patterns: str = "default"


class Language:
    """Centralized language detection and processing from Whisper output"""
    def __init__(self, config: Optional[LanguageConfig] = None):
        self.config = config or LanguageConfig()
        self.detected_language: Optional[str] = None
        debug.dprint(f"Language initialized | Default: {self.config.default_language} | Supported: {self.config.supported_languages}")

    def process_whisper_output(self, transcription_result: Dict[str, Any]) -> None:
        """Process Whisper's output to extract and validate language"""
        debug.dprint(f"Processing transcription result of size: {len(transcription_result)}")

        if not transcription_result or not isinstance(transcription_result, dict):
            debug.dprint("Invalid transcription result; skipping language detection")
            return

        lang_code = transcription_result.get("language")
        if not lang_code or not isinstance(lang_code, str):
            debug.dprint("No valid language code found in transcription result")
            return

        # Clean and extract base language code
        lang = lang_code.lower().split("-")[0]
        debug.dprint(f"Extracted base language code: {lang}")

        # Validate against supported languages
        if lang in self.config.supported_languages:
            self.detected_language = lang
            debug.dprint(f"Detected language set: {self.detected_language}")
        else:
            # Try matching first 2 letters (en, pt, es, etc.)
            base_code = lang[:2]
            for supported_lang in self.config.supported_languages:
                if supported_lang.startswith(base_code):
                    self.detected_language = supported_lang
                    debug.dprint(f"Detected language matched fallback: {self.detected_language}")
                    break
            if not self.detected_language:
                debug.dprint("No matching supported language found; will fallback later")

    def get_language(self) -> str:
        """Get the detected language or fallback to default"""
        detected = self.detected_language or self.config.default_language
        debug.dprint(f"Returning language: {detected}")
        return detected

    def get_language_code(self) -> str:
        """Get 2-letter language code"""
        code = self.get_language()[:2]
        debug.dprint(f"Returning language code: {code}")
        return code

    def is_supported_language(self, lang_code: str) -> bool:
        """Check if a language code is supported"""
        lang = lang_code.lower().split("-")[0]
        is_supported = lang in self.config.supported_languages
        debug.dprint(f"Language '{lang}' is supported: {is_supported}")
        return is_supported

    def get_question_words(self, question_words_map: Dict[str, List[str]]) -> List[str]:
        """Get question words for the current language"""
        lang = self.get_language()
        words = question_words_map.get(lang, question_words_map[self.config.fallback_patterns])
        debug.dprint(f"Question words for language '{lang}': {words}")
        return words

    def get_definition_patterns(self, patterns_map: Dict[str, List[str]]) -> List[str]:
        """Get definition patterns for the current language"""
        lang = self.get_language()
        patterns = patterns_map.get(lang, patterns_map[self.config.fallback_patterns])
        debug.dprint(f"Definition patterns for language '{lang}': {patterns}")
        return patterns


language = Language() 