import os
import re
from typing import Dict, List, Any
from fpdf import FPDF

from src.utils.text.word_snippets import QUESTION_WRD
from src.errors.exceptions import (
    TranscriptionError,
    FileError,
    ErrorCode,
)
from src.errors.logging import log_unexpected_error
from src.frontend.constants import THEMES


class NotesGenerator:
    def __init__(self, language, config):
        self.language = language
        self.config = config

    def create_notes(self, data: Dict[str, Any]) -> str:
        """Guarantees all sections exist, even if empty"""
        if not data.get("text"):
            raise TranscriptionError.no_result()

        text = data["text"]
        segments = data.get("segments", [])

        sections = {
            "Summary": self._generate_summary(text),
            "Key Terms": self._extract_key_terms(segments),
            "Questions": self._extract_questions(segments),
            "Timestamps": self._get_important_timestamps(segments),
        }

        return self._format_as_markdown(sections)

    def _generate_summary(self, text: str) -> str:
        try:
            sentences = re.split(r"(?<=[.!?])\s+", text)
            return " ".join(sentences[:2]) if sentences else text[:200] + "..."
        except Exception as e:
            raise TranscriptionError.sentence_split_failed(e)

    def _extract_key_terms(self, segments: List[Dict]) -> List[str]:
        terms = set()
        for seg in segments:
            for w in re.findall(r"\b[A-Z][a-z]{3,}\b", seg.get("text", "")):
                if w.lower() not in QUESTION_WRD.get("english", []):
                    terms.add(w)
        return sorted(terms)[:10]

    def _extract_questions(self, segments: List[Dict]) -> List[Dict]:
        qs = []
        lang = self.language.get_language_code()
        words = set(QUESTION_WRD.get(lang, QUESTION_WRD.get("english", [])))

        for seg in segments:
            t = seg.get("text", "").strip()
            if t.endswith("?") or any(t.lower().startswith(qw) for qw in words):
                qs.append(
                    {
                        "text": t,
                        "timestamp": self._format_timestamp(seg.get("start", 0)),
                    }
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
        return out[:5]

    def _format_timestamp(self, seconds: float) -> str:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02}:{int(m):02}:{int(s):02}"

    def _format_as_markdown(self, sections: Dict[str, Any]) -> str:
        """Convert to markdown with fallbacks"""
        out = []
        for sec, content in sections.items():
            out.append(f"# {sec}\n")

            if isinstance(content, list):
                if not content:
                    out.append("None found\n")
                elif isinstance(content[0], dict):
                    for item in content:
                        ts = item.get("timestamp", "00:00:00")
                        txt = item.get("text", "[missing]")
                        out.append(f"- **{ts}**: {txt}")
                else:
                    for term in content:
                        out.append(f"- {term}")
            else:
                out.append(content if content.strip() else "None found")

            out.append("")  # spacing

        return "\n".join(out)
