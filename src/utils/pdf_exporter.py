import os
from fpdf import FPDF

from src.errors.exceptions import ErrorCode, FileError
from src.frontend.constants import THEMES, FONT_FALLBACKS


class CustomPDF(FPDF):
    """Custom PDF generator with consistent styling and layout."""
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Arial", size=12)
        self.set_draw_color(*self._hex_to_rgb(THEMES["dark"]["bg"]))
        self.set_line_width(0.5)
        self.line(10, 10, 200, 10)
        self.cell(0, 10, "Made With Emily's Transcriptor", ln=1, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", size=8)
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
        self.font_family = self._init_system_font()
        
    def _init_system_font(self) -> str:
        """Try common system fonts, fail fast if none work."""
        for font in FONT_FALLBACKS:
            try:
                self.pdf.add_font(font, "", f"{font}.ttf", uni=True)
                return font

            except RuntimeError:
                continue

        raise FileError.pdf_font_error(FONT_FALLBACKS)

    def export_to_pdf(self, text: str, filename: str, title: str) -> bool:
        """Render normalized text as a clean, readable PDF."""
        try:
            if not text.strip():
                raise FileError.pdf_invalid_content(len(text))

            self.pdf = CustomPDF()
            self.pdf.add_page()

            # Title block
            self.pdf.set_font(self.font_family, style="B", size=18)
            self.pdf.cell(0, 10, title, ln=1, align="C")
            self.pdf.ln(10)

            # Body rendering
            self.pdf.set_font(self.font_family, size=12)
            for line in text.splitlines():
                self.pdf.multi_cell(0, 6, line or " ")  # Render even empty lines
                self.pdf.ln(3)  # Consistent spacing

            # Ensure output path is valid
            try:
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                
            except PermissionError as e:
                raise FileError.pdf_permission_denied(filename, e) from e
            
            except OSError as e:
                raise FileError(
                    code=ErrorCode.DIRECTORY_CREATION_ERROR,
                    message="Failed to create directory for PDF",
                    context={"path": filename, "original_error": str(e)},
                ) from e

            # Check write access
            try:
                if os.path.exists(filename) and not os.access(filename, os.W_OK):
                    raise PermissionError(f"Write permission denied: {filename}")

            except PermissionError as e:
                raise FileError.pdf_permission_denied(filename, e)

            # Attempt PDF generation
            try:
                self.pdf.output(filename)
            except RuntimeError as e:
                raise FileError.pdf_creation_failed(e) from e

            except Exception as e:
                raise FileError(
                    code=ErrorCode.PDF_GENERATION_ERROR,
                    message="Unexpected PDF generation error",
                    context={"error_type": type(e).__name__, "error_details": str(e)},
                ) from e

            if not os.path.exists(filename):
                raise FileError.pdf_creation_failed()

            return True

        except FileError:
            raise  # Re-raise known errors
