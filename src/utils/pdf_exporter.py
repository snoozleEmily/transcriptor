import os
from typing import Optional
from fpdf import FPDF



class PDFExporter:
    """Handles export of formatted notes to PDF."""
    
    @staticmethod
    def export_to_pdf(content: str, output_path: str, title: Optional[str] = None) -> bool:
        """
        Export text content to PDF file.
        
        Args:
            content: Text content to export
            output_path: Full path for output PDF
            title: Optional title for PDF document
            
        Returns:
            True if export succeeded, False otherwise
        """
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Add title if provided
            if title:
                pdf.set_font(size=14, style='B')
                pdf.cell(200, 10, txt=title, ln=1, align='C')
                pdf.set_font(size=12, style='')
                pdf.ln(10)
            
            # Add main content
            pdf.multi_cell(0, 10, txt=content)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            pdf.output(output_path)
            return True
        except Exception:
            return False