import os
import re
import datetime
from fpdf import FPDF
from threading import Thread
from typing import Optional, Dict, Any


from src.logs.debug import debug
from src.logs.exceptions import FileError, ErrorCode
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
        self.set_auto_page_break(auto=True, margin=30)

    def register_unicode_fonts(self, font_name: str, font_paths: dict):
        """Register all styles of a TTF font dynamically."""
        for style, path in font_paths.items():
            if os.path.isfile(path):
                self.add_font(font_name, style, path, uni=True)
            else:
                debug.dprint(f"Font path not found: {path}")

    def header(self):
        self.set_font(FONT_NAME, size=12)
        self.set_draw_color(*self._hex_to_rgb(PDF_COLORS["header_line"]))
        self.set_line_width(0.5)
        self.line(10, 10, 200, 10)
        self.set_text_color(*self._hex_to_rgb(PDF_COLORS["text"]))
        self.cell(0, 10, "Made With Emily's Transcriptor", ln=1, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font(FONT_NAME, size=8)
        self.set_draw_color(*self._hex_to_rgb(PDF_COLORS["header_line"]))
        self.set_line_width(0.5)
        self.line(10, self.get_y() - 5, 200, self.get_y() - 5)
        self.set_text_color(*self._hex_to_rgb(PDF_COLORS["footer_text"]))
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
        self.set_y(-10)  # Shift date text up
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
        debug.dprint(f"Formatted notes string length: {len(notes)}")

        if not notes.strip():  # Check for empty content
            raise FileError.pdf_invalid_content(len(notes))

        normalized = self._normalize_notes(notes)

        if text.strip():  # Get full transcription text
            normalized += "\n\n# Transcription\n" + text.strip()

        if not self.render_pdf(
            normalized,
            save_path,
            f"Transcription: {os.path.splitext(os.path.basename(save_path))[0]}",  # Title
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
        # Keep printable ASCII + newline
        return re.sub(r"[^\x20-\x7E\n]", "", text)

    def _format_notes_dict(
        self, notes_dict: Dict[str, Any], odd_words: Optional[dict] = None
    ) -> str:
        """Convert notes dictionary to formatted string for PDF."""
        lines = []

        summary = notes_dict.get("Summary", "")
        if summary:
            lines.append("# Summary\n" + summary + "\n")

        key_terms = notes_dict.get("Key Terms", [])
        if key_terms:
            lines.append("# Key Terms")
            for term in key_terms:
                lines.append(f"- {term}")
            lines.append("")

        if odd_words:
            lines.append("# Specific Words")
            for word, variants in odd_words.items():
                if variants:
                    lines.append(f"- {word}: {', '.join(variants)}")
                else:
                    lines.append(f"- {word}")
            lines.append("")

        questions = notes_dict.get("Questions", [])
        if questions:
            lines.append("# Questions")
            for q in questions:
                lines.append(f"- [{q.get('timestamp', '')}] {q.get('text', '')}")
            lines.append("")

        timestamps = notes_dict.get("Timestamps", [])
        if timestamps:
            lines.append("# Timestamps")
            for t in timestamps:
                lines.append(f"- [{t.get('timestamp', '')}] {t.get('text', '')}")
            lines.append("")

        return "\n".join(lines)

    # ----------------- Export -----------------
    def export_notes_to_pdf(
        self,
        sections: Dict[str, Any],
        output_path: str,
        title: str = "Transcription Notes",
        async_export: bool = False,
    ):
        """Export notes to PDF. Can run asynchronously to avoid GUI freeze."""
        debug.dprint(f"Exporting notes to PDF: {output_path} (async={async_export})")
        if async_export:
            thread = Thread(
                target=self._export_pdf, args=(sections, output_path, title)
            )
            thread.start()
            return thread
        else:
            return self._export_pdf(sections, output_path, title)

    def _export_pdf(self, sections: Dict[str, Any], output_path: str, title: str):
        pdf = self.pdf
        font = self.font_family
        pdf.add_page()

        # Title
        pdf.set_font(font, style="B", size=18)
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(8)

        for section_name, content in sections.items():
            debug.dprint(
                f"Rendering section: {section_name} ({len(content) if isinstance(content, list) else 'str'})"
            )

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
                        pdf.set_font(font, style="B", size=12)
                        pdf.cell(0, 10, f"{ts}:", ln=False)
                        pdf.set_font(font, style="", size=12)
                        pdf.cell(0, 10, f" {txt}", ln=True)
                else:
                    for term in content:
                        pdf.cell(0, 10, f"- {term}", ln=True)
            else:
                pdf.multi_cell(0, 8, content.strip() if content else "None found")

            pdf.ln(5)

        self.pdf = pdf
        debug.dprint(
            f"PDF page content prepared, calling render_pdf for: {output_path}"
        )
        return self.render_pdf(" ", output_path, title)


    # -----------------  Low-level PDF rendering -----------------

    def render_pdf(self, text: str, filename: str, title: str) -> bool:
        try:
            if not text.strip():
                raise FileError.pdf_invalid_content(len(text))

            debug.dprint(f"Starting to render PDF")

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
                    self.pdf.set_text_color(
                        *self.pdf._hex_to_rgb(PDF_COLORS["heading"])
                    )
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
            debug.dprint(
                f"Ensured output directory exists: {os.path.dirname(filename)}"
            )

            if os.path.exists(filename) and not os.access(filename, os.W_OK):
                raise FileError.pdf_permission_denied(filename, PermissionError())

            self.pdf.output(filename)

            if not os.path.exists(filename):
                raise FileError.pdf_creation_failed()

            debug.dprint(
                f"PDF output called. Exists in Path={os.path.exists(filename)}"
            )
            return True

        except FileError:
            raise  # Re-raise previous errors

        except Exception as e:
            raise FileError(
                code=ErrorCode.PDF_GENERATION_ERROR,
                message="Unexpected PDF generation error",
                context={"error_type": type(e).__name__, "error_details": str(e)},
            ) from e
