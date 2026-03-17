import os, glob, PyPDF2

class FilesModule:
    @staticmethod
    def read_pdf(file_path):
        if not os.path.exists(file_path): return "File not found."
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return "".join([p.extract_text() for p in reader.pages[:5]])
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def open_document(name):
        matches = glob.glob(os.path.join(os.path.expanduser("~"), "Documents", f"*{name}*"))
        if matches:
            os.startfile(matches[0])
            return f"Opening {os.path.basename(matches[0])}"
        return "Not found."
