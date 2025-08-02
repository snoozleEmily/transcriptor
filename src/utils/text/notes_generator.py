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
        if not data.get('text'):
            raise TranscriptionError.no_result()

        text = data['text']
        segments = data.get('segments', [])

        sections = {
            'Summary': self._generate_summary(text),
            'Key Terms': self._extract_key_terms(segments),
            'Questions': self._extract_questions(segments),
            'Timestamps': self._get_important_timestamps(segments),
        }

        return self._format_as_markdown(sections)

    def _generate_summary(self, text: str) -> str:
        try:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            return ' '.join(sentences[:2]) if sentences else text[:200] + "..."
        except Exception as e:
            raise TranscriptionError.sentence_split_failed(e)

    def _extract_key_terms(self, segments: List[Dict]) -> List[str]:
        terms = set()
        for seg in segments:
            for w in re.findall(r'\b[A-Z][a-z]{3,}\b', seg['text']):
                if w.lower() not in QUESTION_WRD.get('english', []):
                    terms.add(w)
        return sorted(terms)[:10]

    def _extract_questions(self, segments: List[Dict]) -> List[Dict]:
        qs = []
        lang = self.language.get_language_code()
        words = set(QUESTION_WRD.get(lang, QUESTION_WRD.get('english', [])))

        for seg in segments:
            t = seg['text'].strip()
            if t.endswith('?') or any(t.lower().startswith(qw) for qw in words):
                qs.append({'text': t, 'timestamp': self._format_timestamp(seg['start'])})

        return qs[:5]

    def _get_important_timestamps(self, segments: List[Dict]) -> List[Dict]:
        out = []
        for seg in segments:
            if len(seg['text'].split()) > 10:
                snippet = seg['text'][:100] + ('...' if len(seg['text']) > 100 else '')
                out.append({'text': snippet, 'timestamp': self._format_timestamp(seg['start'])})
        return out[:5]

    def _format_timestamp(self, seconds: float) -> str:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02}:{int(m):02}:{int(s):02}"

    def _format_as_markdown(self, sections: Dict[str, Any]) -> str:
        out = []
        for sec, content in sections.items():
            out.append(f"# {sec}\n\n")
            if isinstance(content, list):
                if not content:
                    out.append("None found\n\n")
                elif isinstance(content[0], dict):
                    for item in content:
                        ts = item.get('timestamp', '00:00:00')
                        txt = item.get('text', '[missing]')
                        out.append(f"- **{ts}**: {txt}\n")
                    out.append("\n")
                else:
                    for term in content:
                        out.append(f"- {term}\n")
                    out.append("\n")
            else:
                out.append(f"{content}\n\n")
        return "".join(out)


class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        # register Unicode font
        self.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)

    def header(self):
        r, g, b = self._hex_to_rgb(THEMES["dark"]["bg"])
        self.set_draw_color(r, g, b)
        self.set_line_width(0.5)
        self.line(10, 10, 200, 10)
        self.set_font("DejaVu", size=12)
        self.cell(0, 10, "Made With Emily's Transcriptor", ln=1, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        r, g, b = self._hex_to_rgb(THEMES["dark"]["bg"])
        self.set_draw_color(r, g, b)
        self.set_line_width(0.5)
        self.line(10, self.get_y()-2, 200, self.get_y()-2)
        self.set_font("DejaVu", size=8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        h = hex_color.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


class PDFExporter:
    def __init__(self):
        self.pdf = CustomPDF()

    def export_to_pdf(self, text: str, filename: str, title: str) -> bool:
        try:
            if not isinstance(text, str) or not text.strip():
                raise FileError.pdf_invalid_content(len(text))

            self.pdf = CustomPDF()
            self.pdf.add_page()

            # Title
            self.pdf.set_font("DejaVu", style="B", size=18)
            self.pdf.cell(0, 10, title, ln=1, align="C")
            self.pdf.ln(10)
            self.pdf.set_font("DejaVu", size=12)

            # Content
            for line in text.splitlines():
                if line.startswith("# "):
                    self.pdf.set_font(style="B", size=16)
                    self.pdf.cell(0, 10, line[2:], ln=1)
                    self.pdf.set_font(size=12)
                elif line.startswith("- **"):
                    self.pdf.set_font(style="B", size=12)
                    self.pdf.cell(0, 8, line, ln=1)
                    self.pdf.set_font(size=12)
                elif line.startswith("- "):
                    self.pdf.cell(10)
                    self.pdf.cell(0, 8, line[2:], ln=1)
                else:
                    if line:
                        self.pdf.multi_cell(0, 6, line)
                    else:
                        self.pdf.ln(4)

            # Ensure directory
            try:
                os.makedirs(os.path.dirname(filename), exist_ok=True)
            except PermissionError as e:
                raise FileError.pdf_permission_denied(filename, e)
            except OSError as e:
                raise FileError(
                    code=ErrorCode.DIRECTORY_CREATION_ERROR,
                    message="Failed to create directory for PDF",
                    context={"path": filename, "original_error": str(e)}
                )

            # Write file
            try:
                self.pdf.output(filename)
            except PermissionError as e:
                raise FileError.pdf_permission_denied(filename, e)
            except Exception as e:
                raise FileError.pdf_creation_failed(e)

            # Post-check
            if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                raise FileError.pdf_creation_failed(None)

            return True

        except FileError:
            # propagate your FileError with emoji and code
            raise
        except Exception as e:
            log_unexpected_error(e)
            raise FileError.pdf_creation_failed(e)
