import re
from typing import Dict, List, Any



from src.errors.debug import debug
from src.errors.exceptions import TranscriptionError
from src.utils.pdf_maker import PDFExporter
from src.utils.text.words.common import COMMON_WORDS
from src.utils.text.words.question import QUESTION_WRD
from src.utils.text.language import Language



class NotesGenerator:
    def __init__(self, language, config):
        self.language = Language()
        self.config = config
        self.pdf_exporter = PDFExporter()

        debug.dprint(f"NotesGenerator initialized with config: {config}, language: {language}")


    def create_notes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepares all sections as a dict, even if empty"""
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

        return sections

    def export_notes_to_pdf(
        self,
        sections: Dict[str, Any],
        output_path: str,
        title: str = "Transcription Notes",
    ):
        from src.utils.pdf_maker import CustomPDF  # avoid circular import

        pdf = self.pdf_exporter.pdf
        font = self.pdf_exporter.font_family
        debug.dprint(f"Font: {font}")
        pdf.add_page()

        # Title
        pdf.set_font(font, style="B", size=18)
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(8)

        for section_name, content in sections.items():
            # Section header
            pdf.set_font(font, style="B", size=16)
            pdf.cell(0, 10, section_name.upper(), ln=True)
            pdf.ln(2)

            # Section content
            pdf.set_font(font, style="", size=12)

            if isinstance(content, list):
                if not content:
                    pdf.cell(0, 10, "None found", ln=True)

                elif isinstance(content[0], dict):
                    for item in content:
                        ts = item.get("timestamp", "00:00:00")
                        txt = item.get("text", "[missing]")

                        # Timestamp in bold
                        pdf.set_font(font, style="B", size=12)
                        pdf.cell(0, 10, f"{ts}:", ln=False)

                        # Text normal
                        pdf.set_font(font, style="", size=12)
                        pdf.cell(0, 10, f" {txt}", ln=True)

                else:
                    for term in content:
                        pdf.cell(0, 10, f"- {term}", ln=True)

            else:
                pdf.multi_cell(0, 8, content.strip() if content else "None found")

            pdf.ln(5)

            self.pdf_exporter.pdf = pdf
            return self.pdf_exporter.render_pdf(
                " ", output_path, title
            )  # dummy text param

    def _generate_summary(self, text: str) -> str:
        try:
            sentences = re.split(r"(?<=[.!?])\s+", text)
            return " ".join(sentences[:2]) if sentences else text[:200] + "..."

        except Exception as e:
            raise TranscriptionError.sentence_split_failed(e)

    def _extract_key_terms(self, segments: List[Dict]) -> List[str]:
        terms = set()
        lang = self.language.get_language()
        excluded_words = set(QUESTION_WRD.get(lang, []) + COMMON_WORDS.get(lang, []))

        for seg in segments:
            words = re.findall(r"\b[A-Z][a-z]{3,}\b", seg.get("text", ""))
            for w in words:
                if w.lower() not in excluded_words: # TODO: add skip from custom_words
                    terms.add(w)

        return sorted(terms)[:8]

    def _extract_questions(self, segments: List[Dict]) -> List[Dict]:
        qs = []
        lang = self.language.get_language_code()
        question_words = set(QUESTION_WRD.get(lang, QUESTION_WRD["default"]))

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
