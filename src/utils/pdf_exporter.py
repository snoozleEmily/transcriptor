import os
from fpdf import FPDF


from src.errors.exceptions import ErrorCode, FileError
from src.frontend.constants import THEMES



class CustomPDF(FPDF):
    """Custom PDF class with consistent header/footer styling"""
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        """Add header to each page"""
        self.set_font("Arial", size=12)
        self.set_draw_color(*self._hex_to_rgb(THEMES["dark"]["bg"]))
        self.set_line_width(0.5)
        self.line(10, 10, 200, 10)
        self.cell(0, 10, "Made With Emily's Transcriptor", ln=1, align="C")
    
    def footer(self):
        """Add footer to each page"""
        self.set_y(-15)
        self.set_font("Arial", size=8)
        self.set_draw_color(*self._hex_to_rgb(THEMES["dark"]["bg"]))
        self.set_line_width(0.5)
        self.line(10, self.get_y()-2, 200, self.get_y()-2)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
    
    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB values"""
        hex_color = hex_color.lstrip('#')
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16), 
            int(hex_color[4:6], 16)
)

class PDFExporter:
    """Handles PDF generation and export"""
    def __init__(self):
        self.pdf = CustomPDF()
    
    def export_to_pdf(self, text: str, filename: str, title: str) -> bool:
        """Export text content to PDF file"""
        try:
            self.pdf = CustomPDF()  # Fresh instance for each export
            self.pdf.add_page()
            
            # Add title
            self.pdf.set_font(size=18, style="B")
            self.pdf.cell(0, 10, title, ln=1, align="C")
            self.pdf.ln(10)
            
            # Process content
            self.pdf.set_font(size=12)
            for line in text.split('\n'):
                line = line.strip()
                
                if line.startswith("# "):
                    self.pdf.set_font(size=14, style="B")
                    self.pdf.cell(0, 10, line[2:], ln=1)
                    self.pdf.set_font(size=12)

                elif line.startswith("• "):
                    self.pdf.cell(10)
                    self.pdf.cell(0, 10, line[2:], ln=1)
                    
                elif line.startswith("  - "):
                    self.pdf.cell(20)
                    self.pdf.cell(0, 10, line[4:], ln=1)

                else:
                    self.pdf.ln(5)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.pdf.output(filename)
            return os.path.exists(filename)
            
        except Exception as e:
            raise FileError(
                code=ErrorCode.FILE_ERROR,
                message=f"PDF export failed: {str(e)}"
            )