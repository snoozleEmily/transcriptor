import os
from fpdf import FPDF


from src.errors.exceptions import FileError, ErrorCode



class PDFExporter:
    def export_to_pdf(self, notes: str, filename: str, title: str = "Notes") -> bool:
        """Language-agnostic PDF formatting with error handling"""
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Set default font with UTF-8 support
            pdf.set_font("Arial", size=12)

            # Add title
            pdf.set_font(size=18, style="B")
            pdf.cell(0, 10, txt=title, ln=1, align="C")
            pdf.ln(10)
            pdf.set_font(size=12, style="")

            # Process each line
            for line in notes.split("\n"):
                if line.startswith("# "):
                    pdf.set_font(size=14, style="B")
                    pdf.cell(0, 10, txt=line[2:], ln=1)
                    pdf.set_font(size=12, style="")

                elif line.startswith("• "):
                    pdf.cell(10)
                    pdf.cell(0, 10, txt=line[2:], ln=1)

                elif line.startswith("  - "):
                    pdf.cell(20)
                    pdf.cell(0, 10, txt=line[4:], ln=1)
                    
                else:
                    pdf.ln(5)

            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Save the PDF
            pdf.output(filename)
            return os.path.exists(filename)
            
        except Exception as e:
            raise FileError(
                code=ErrorCode.FILE_ERROR,
                message=f"Error genarating PDF, becasue of {e}"
            )