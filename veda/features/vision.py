import os
from PIL import Image
try:
    import PyPDF2
    PDF_LIBS = True
except ImportError:
    PDF_LIBS = False

class VisionPlugin:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "extract_pdf": self.extract_pdf_text,
            "image_info": self.get_image_data
        }

    def extract_pdf_text(self, params):
        if not PDF_LIBS: return "PDF intelligence module missing."
        path = params.get("path")
        if not path or not os.path.exists(path): return "Invalid path."

        try:
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in range(min(3, len(reader.pages))):
                    text += reader.pages[page].extract_text()
                return f"Content extracted (first 3 pages):\n{text[:500]}..."
        except Exception as e:
            return f"Extraction failed: {e}"

    def get_image_data(self, params):
        path = params.get("path")
        if not path or not os.path.exists(path): return "Invalid path."

        try:
            with Image.open(path) as img:
                return f"Image Intel: Format: {img.format}, Size: {img.size}, Mode: {img.mode}"
        except Exception as e:
            return f"Vision link failed: {e}"
