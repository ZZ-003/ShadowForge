import os
import hashlib


def _patch_md5_usedforsecurity_compat():
    """Make reportlab compatible with runtimes lacking md5(usedforsecurity=...)."""
    try:
        hashlib.md5(usedforsecurity=False)
    except TypeError:
        original_md5 = hashlib.md5

        def compat_md5(*args, **kwargs):
            kwargs.pop("usedforsecurity", None)
            return original_md5(*args, **kwargs)

        hashlib.md5 = compat_md5


_patch_md5_usedforsecurity_compat()

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY

class PDFGenerator:
    def __init__(self, font_name="Helvetica", font_size=12):
        self.font_name = font_name
        self.font_size = font_size

    def generate_pdf(self, text, output_path, secret=None, secret_placeholder="SECRET_HERE"):
        """
        Generates a PDF document from text.
        """
        if secret and secret_placeholder in text:
            final_text = text.replace(secret_placeholder, secret)
        else:
            final_text = text
            
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=18)
            
            Story = []
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
            
            # Simple parsing: 
            # If line starts with # -> Heading
            # Else -> Paragraph
            
            lines = final_text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    Story.append(Spacer(1, 12))
                    continue
                    
                if line.startswith('# '):
                    # H1
                    ptext = line[2:]
                    Story.append(Paragraph(ptext, styles["Heading1"]))
                elif line.startswith('## '):
                    # H2
                    ptext = line[3:]
                    Story.append(Paragraph(ptext, styles["Heading2"]))
                else:
                    # Normal
                    Story.append(Paragraph(line, styles["Normal"]))
                
                Story.append(Spacer(1, 12))
                
            doc.build(Story)
            return output_path
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
