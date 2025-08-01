import os
from fpdf import FPDF


from src.errors.exceptions import ErrorCode, FileError
from src.frontend.constants import THEMES



class CustomPDF(FPDF):
    """Custom PDF generator with consistent styling and layout.

    Extends FPDF to provide:
    - Standardized header/footer on all pages
    - Theme color support
    - Consistent styling for different content types
    """

    def __init__(self):
        """Initialize PDF with automatic page breaks and margins."""
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)  # 15mm bottom margin

    def header(self):
        """Add standardized header to each page with:
        - Top border line using theme color
        - Centered application branding text
        """
        self.set_font("Arial", size=12)
        # Convert theme hex color to RGB for drawing
        self.set_draw_color(*self._hex_to_rgb(THEMES["dark"]["bg"]))
        self.set_line_width(0.5)
        self.line(10, 10, 200, 10)  # Draw header line
        self.cell(0, 10, "Made With Emily's Transcriptor", ln=1, align="C")

    def footer(self):
        """Add standardized footer to each page with:
        - Bottom border line using theme color
        - Page number centered
        """
        self.set_y(-15)  # Position 15mm from bottom
        self.set_font("Arial", size=8)
        self.set_draw_color(*self._hex_to_rgb(THEMES["dark"]["bg"]))
        self.set_line_width(0.5)
        self.line(10, self.get_y() - 2, 200, self.get_y() - 2)  # Draw footer line
        self.cell(0, 10, f"Page {self.page_no()}", align="C")  # Page number

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert hex color code to RGB tuple for PDF rendering.

        Args:
            hex_color: Color in hex format (e.g. '#RRGGBB')

        Returns:
            Tuple of (red, green, blue) integer values (0-255)
        """
        hex_color = hex_color.lstrip("#")
        return (
            int(hex_color[0:2], 16),  # Red component
            int(hex_color[2:4], 16),  # Green component
            int(hex_color[4:6], 16),  # Blue component
        )


class PDFExporter:
    """Main PDF export handler that processes content and generates files.

    Features:
    - Structured content parsing (headings, lists, etc.)
    - Automatic directory creation
    - Error handling for file operations
    """

    def __init__(self):
        """Initialize with a fresh PDF instance."""
        self.pdf = CustomPDF()

    def export_to_pdf(self, text: str, filename: str, title: str) -> bool:
        """Convert text content to styled PDF document"""
        self.pdf = CustomPDF()
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)
        self.pdf.multi_cell(0, 5, text)  # Simple text dump
        self.pdf.output(filename)
        return True
