import re
from typing import Dict, List, Any, Optional


from src.logs.debug import debug
from src.logs.exceptions import TranscriptionError
from src.utils.text.language import Language
from src.utils.text.llama import llama, Llama
from src.utils.text.words.common import COMMON_WORDS
from src.utils.text.words.question import QUESTION_WRD




class NotesGenerator:
    def __init__(self, language, config: Any):
        self.language: Language = language
        self.config = config
        self.llama: Llama = llama

        debug.dprint(
            f"NotesGenerator initialized with config: {config}, language: {language}"
        )

    # ----------------- Notes Generation -----------------
    def create_notes(
        self, data: Dict[str, Any], max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Prepares all sections as a dict, even if empty"""
        if not data.get("text"):
            raise TranscriptionError.no_result()

        text = data["text"]
        segments = data.get("segments", [])

        sections = {
            "Summary": self._generate_summary(text, max_tokens),
            "Key Terms": self._extract_key_terms(segments),
            "Questions": self._extract_questions(segments),
            "Timestamps": self._get_important_timestamps(segments),
        }

        return sections

    # ----------------- Helpers -----------------
    def _generate_summary(self, text: str, max_tokens: int) -> str:
        try:
            debug.dprint(f"Inside _generate_summary. Language is: {self.language}")
            debug.dprint(f"Generating summary with LLaMA for text length={len(text)}")
            return self.llama.summarize_text(text, max_tokens)

        except Exception as e:
            debug.dprint(f"Using fallback since LLaMA summarization failed: {e}")
            sentences = re.split(r"(?<=[.!?])\s+", text)
            return " ".join(sentences[:2]) + ("..." if len(sentences) > 2 else "")

    def _extract_key_terms(self, segments: List[Dict]) -> List[str]:
        terms = set()
        lang = self.language.get_language()
        excluded_words = set(QUESTION_WRD.get(lang, []) + COMMON_WORDS.get(lang, []))

        debug.dprint(f"Inside _extract_key_terms. Language is: {lang}")

        for seg in segments:
            words = re.findall(r"\b[A-Z][a-z]{3,}\b", seg.get("text", ""))
            for w in words:
                if w.lower() not in excluded_words:
                    terms.add(w)

        return sorted(terms)[:8]

    def _extract_questions(self, segments: List[Dict]) -> List[Dict]:
        qs = []
        lang = self.language.get_language_code()
        question_words = set(QUESTION_WRD.get(lang, QUESTION_WRD.get("default", [])))

        debug.dprint(f"Inside _extract_questions. Language is: {lang}")

        for seg in segments:
            t = seg.get("text", "").strip()
            if t.endswith("?") or any(
                t.lower().startswith(qw) for qw in question_words
            ):
                qs.append(
                    {
                        "text": t,
                        "timestamp": self._format_timestamp(seg.get("start", 0)),
                    }
                )

        debug.dprint(
            f"Detected questions: {len(qs)}" if qs else "No questions detected"
        )
        return qs[:5]

    def _get_important_timestamps(self, segments: List[Dict]) -> List[Dict]:
        out = []
        for seg in segments:
            txt = seg.get("text", "")
            if len(txt.split()) > 10:
                snippet = txt[:100] + ("..." if len(txt) > 100 else "")
                out.append(
                    {
                        "text": snippet,
                        "timestamp": self._format_timestamp(seg.get("start", 0)),
                    }
                )

        debug.dprint(
            f"Important parts found: {len(out)}"
            if out
            else "No important snippets added"
        )
        return out[:5]

    def _format_timestamp(self, seconds: float) -> str:
        seconds = seconds or 0
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02}:{int(m):02}:{int(s):02}"