import os
from fpdf import FPDF


from src.errors.exceptions import FileError, ErrorCode
from src.frontend.constants import THEMES


class PDFExporter:
    pdf = FPDF()

    def header(self):
        PDFExporter.pdf.set_font("Arial", size=12)

        # Decorative line on top
        self.set_draw_color(THEMES["dark"]["bg"]) 
        self.set_line_width(0.5)
        self.line(10, 10, 200, 10)
        self.cell(0, 10, "Made With Emily's Transcriptor", ln=True, align="C")
                  
    def footer(self):
        self.set_y(-15)  # Position 1.5 cm from bottom
        PDFExporter.pdf.set_font("Arial", size=8)

        # Decorative line above footer
        self.set_draw_color(THEMES["dark"]["bg"]) 
        self.set_line_width(0.5)
        self.line(10, self.get_y() - 2, 200, self.get_y() - 2)

        # Page number
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def export_to_pdf(self, notes: str, filename: str, title: str = "Notes") -> bool:
        try:
            print(f"Starting PDF export to '{filename}' with title '{title}'")
            PDFExporter.pdf.add_page()
            print("\nAdded new page")

            # Add title
            PDFExporter.pdf.set_font(size=18, style="B")
            PDFExporter.pdf.cell(0, 10, txt=title, ln=1, align="C")
            PDFExporter.pdf.ln(10)
            PDFExporter.pdf.set_font(size=12, style="")
            print(f"Title '{title}' added")

            # Process each line
            lines = notes.split("\n")
            print(f"\nProcessing {len(lines)} lines of notes")
            line_counts = {'headers': 0, 'bullets': 0, 'sub_bullets': 0}
            for line in lines:
                line = line.strip()
                if line.startswith("# "):
                    PDFExporter.pdf.set_font(size=14, style="B")
                    PDFExporter.pdf.cell(0, 10, txt=line[2:], ln=1)
                    PDFExporter.pdf.set_font(size=12, style="")
                    line_counts['headers'] += 1

                elif line.startswith("• "):
                    PDFExporter.pdf.cell(10)
                    PDFExporter.pdf.cell(0, 10, txt=line[2:], ln=1)
                    line_counts['bullets'] += 1

                elif line.startswith("  - "):
                    PDFExporter.pdf.cell(20)
                    PDFExporter.pdf.cell(0, 10, txt=line[4:], ln=1)
                    line_counts['sub_bullets'] += 1
                else:
                    PDFExporter.pdf.ln(5)

            print(f"\nProcessed lines: {line_counts}")

            # Ensure directory exists
            dir_path = os.path.dirname(filename)
            print(f"\nCreating directory: '{dir_path}'")
            os.makedirs(dir_path, exist_ok=True)

            # Save the PDF
            print(f"\nSaving PDF to '{filename}'")
            PDFExporter.pdf.output(filename)

            print("\nPDF saved. Verifying file existence...")
            file_exists = os.path.exists(filename)

            print(f"\nFile exists: {file_exists}")
            return file_exists
        
        except Exception as e:
            raise FileError(
                code=ErrorCode.FILE_ERROR,
                message=f"Error during PDF export: {e}"
            )
