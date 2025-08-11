import os
from fpdf import FPDF
from typing import Optional, Dict, Any


from src.errors.exceptions import FileError, ErrorCode
from src.frontend.constants import THEMES



FONT_NAME = "DejaVu" # Unicode safe
FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")

FONT_PATHS = {
    "": os.path.join(FONT_DIR, "DejaVuSans.ttf"),               # Regular
    "B": os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"),         # Bold
    "I": os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf"),      # Italic
    "BI": os.path.join(FONT_DIR, "DejaVuSans-BoldOblique.ttf"), # Bold Italic
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
        self.set_draw_color(*self._hex_to_rgb(THEMES["dark"]["bg"]))
        self.set_line_width(0.5)
        self.line(10, 10, 200, 10)
        self.cell(0, 10, "Made With Emily's Transcriptor", ln=1, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font(FONT_NAME, size=8)
        self.set_draw_color(*self._hex_to_rgb(THEMES["dark"]["bg"]))
        self.set_line_width(0.5)
        self.line(10, self.get_y() - 2, 200, self.get_y() - 2)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

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

    def export_to_pdf(self, text: str, filename: str, title: str, odd_words: Optional[dict] = None) -> bool:
        try:
            if not text.strip():
                raise FileError.pdf_invalid_content(len(text))

            self.pdf = CustomPDF()
            self.font_family = self._load_unicode_fonts()
            self.pdf.add_page()

            # Title block
            self.pdf.set_font(self.font_family, style="B", size=18)
            self.pdf.cell(0, 10, title, ln=1, align="C")
            self.pdf.ln(10)

            # Body rendering
            self.pdf.set_font(self.font_family, size=12)
            for line in text.splitlines():
                self.pdf.multi_cell(0, 6, line or " ")
                self.pdf.ln(3)

            # Ensure output path is valid
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            if os.path.exists(filename) and not os.access(filename, os.W_OK):
                raise FileError.pdf_permission_denied(filename, PermissionError())

            self.pdf.output(filename)

            if not os.path.exists(filename):
                raise FileError.pdf_creation_failed()

            return True

        except FileError:
            raise # Re-raise already formatted error
        
        except Exception as e:
            raise FileError(
                code=ErrorCode.PDF_GENERATION_ERROR,
                message="Unexpected PDF generation error",
                context={"error_type": type(e).__name__, "error_details": str(e)},
            ) from e
