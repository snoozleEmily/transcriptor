import os
import re
import datetime
from fpdf import FPDF
from typing import Optional, Dict, Any

from src.errors.exceptions import FileError, ErrorCode
from src.frontend.constants import PDF_COLORS



FONT_NAME = "DejaVu"  # Unicode safe
FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")
FONT_PATHS = {
    "": os.path.join(FONT_DIR, "DejaVuSans.ttf"),  # Regular
    "B": os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"),  # Bold
    "I": os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf"),  # Italic
    "BI": os.path.join(FONT_DIR, "DejaVuSans-BoldOblique.ttf"),  # Bold Italic
}


class CustomPDF(FPDF):
    """Custom PDF generator with consistent styling and layout."""
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def register_unicode_fonts(self, font_name: str, font_paths: dict):
        """Register all styles of a TTF font dynamically."""
        for style, path in font_paths.items():
            if os.path.isfile(path):
                self.add_font(font_name, style, path, uni=True)

    def header(self):
        self.set_font(FONT_NAME, size=12)
        self.set_draw_color(*self._hex_to_rgb(PDF_COLORS["header_line"]))
        self.set_line_width(0.5)
        self.line(10, 10, 200, 10)
        self.set_text_color(*self._hex_to_rgb(PDF_COLORS["text"]))
        self.cell(0, 10, "Made With Emily's Transcriptor", ln=1, align="C")

    def footer(self):
        self.set_y(-30)  # Increase margin by moving footer content higher
        self.set_font(FONT_NAME, size=8)
        self.set_draw_color(*self._hex_to_rgb(PDF_COLORS["header_line"]))
        self.set_line_width(0.5)
        self.line(10, self.get_y() - 2, 200, self.get_y() - 2)
        self.set_text_color(*self._hex_to_rgb(PDF_COLORS["footer_text"]))
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
        self.set_y(-25)  # Also shift date text up
        date_str = datetime.datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 10, f"Generated on: {date_str}", align="C")

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.lstrip("#")
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )


class PDFExporter:
    """Main PDF export handler that processes content and generates files."""
    def __init__(self):
        self.pdf = CustomPDF()
        self.font_family = self._load_unicode_fonts()

    def _load_unicode_fonts(self) -> str:
        self.pdf.register_unicode_fonts(FONT_NAME, FONT_PATHS)
        return FONT_NAME

    def save_notes(
        self,
        result: Dict[str, Any],
        text: str,
        save_path: str,
        odd_words: Optional[dict] = None,
        language=None,
        config=None,
    ) -> None:
        """Handle PDF export with normalization and validation."""
        from src.utils.text.notes_generator import NotesGenerator

        notes_generator = NotesGenerator(language=language, config=config)
        notes_dict = notes_generator.create_notes(
            {"text": text, "segments": result.get("segments", [])}
        )

        notes = self._format_notes_dict(notes_dict, odd_words)

        if not notes.strip():  # Check for empty content
            raise FileError.pdf_invalid_content(len(notes))

        normalized = self._normalize_notes(notes)

        if text.strip(): # Get full transcription text
            normalized += "\n\n# Transcription\n" + text.strip()

        if not self.render_pdf(
            normalized, save_path,
            f"Transcription: {os.path.splitext(os.path.basename(save_path))[0]}"  # Title
        ):
            raise FileError.pdf_creation_failed()

    def _normalize_notes(self, notes: str) -> str:
        """Standardize PDF rendering."""
        lines = []
        for line in notes.splitlines():
            line = line.rstrip()

            # Convert bullets
            if line.lstrip().startswith("•"):
                line = line.replace("•", "-", 1)

            # Normalize headers (reduce multiple '#' to single '#')
            if line.startswith(("#", "##", "###")):
                line = f"# {line.lstrip('# ').strip()}"

            lines.append(line)

        return "\n".join(lines)

    def _clean_text(self, text: str) -> str:
        """Remove problematic or non-printable characters for PDF."""
        # Keep printable ASCII + newline (adjust if you want unicode)
        return re.sub(r"[^\x20-\x7E\n]", "", text)

    def _format_notes_dict(
        self, notes_dict: Dict[str, Any], odd_words: Optional[dict] = None
    ) -> str:
        """Convert notes dictionary to formatted string for PDF."""
        lines = []

        # Add summary
        summary = notes_dict.get("Summary", "")
        if summary:
            lines.append("# Summary\n" + summary + "\n")

        # Add Key Terms as bullet points
        key_terms = notes_dict.get("Key Terms", [])
        if key_terms:
            lines.append("# Key Terms")
            for term in key_terms:
                lines.append(f"- {term}")
            lines.append("")

        # Add Odd Words after Key Terms
        if odd_words:
            lines.append("# Specific Words")
            for word, variants in odd_words.items():
                if variants:
                    lines.append(f"- {word}: {', '.join(variants)}")
                else:
                    lines.append(f"- {word}")
            lines.append("")

        # Add Questions with timestamps
        questions = notes_dict.get("Questions", [])
        if questions:
            lines.append("# Questions")
            for q in questions:
                lines.append(f"- [{q.get('timestamp', '')}] {q.get('text', '')}")
            lines.append("")

        # Add Timestamps with text
        timestamps = notes_dict.get("Timestamps", [])
        if timestamps:
            lines.append("# Timestamps")
            for t in timestamps:
                lines.append(f"- [{t.get('timestamp', '')}] {t.get('text', '')}")
            lines.append("")

        return "\n".join(lines)
    
    def render_pdf(self, text: str, filename: str, title: str) -> bool:
        try:
            if not text.strip():
                raise FileError.pdf_invalid_content(len(text))

            self.pdf = CustomPDF()
            self.font_family = self._load_unicode_fonts()
            self.pdf.add_page()

            # Title block
            self.pdf.set_text_color(*self.pdf._hex_to_rgb(PDF_COLORS["title"]))
            self.pdf.set_font(self.font_family, style="B", size=18)
            self.pdf.cell(0, 10, title, ln=1, align="C")
            self.pdf.ln(10)

            cleaned_text = self._normalize_notes(text)

            # Body rendering
            for line in cleaned_text.splitlines():
                line = line.strip()

                if line.startswith("# "):  # Heading 
                    self.pdf.set_text_color(*self.pdf._hex_to_rgb(PDF_COLORS["heading"]))
                    self.pdf.set_font(self.font_family, style="B", size=14)
                    self.pdf.multi_cell(0, 8, line[2:].strip())
                    self.pdf.ln(2)

                else:  # Regular text
                    self.pdf.set_text_color(*self.pdf._hex_to_rgb(PDF_COLORS["text"]))
                    self.pdf.set_font(self.font_family, size=12)
                    self.pdf.multi_cell(0, 6, line or " ")
                    self.pdf.ln(2)

            # Ensure output path is valid
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            if os.path.exists(filename) and not os.access(filename, os.W_OK):
                raise FileError.pdf_permission_denied(filename, PermissionError())

            self.pdf.output(filename)

            if not os.path.exists(filename):
                raise FileError.pdf_creation_failed()

            return True

        except FileError:
            raise  # Re-raise previous errors

        except Exception as e:
            raise FileError(
                code=ErrorCode.PDF_GENERATION_ERROR,
                message="Unexpected PDF generation error",
                context={"error_type": type(e).__name__, "error_details": str(e)},
            ) from e
