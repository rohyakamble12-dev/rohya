import os, glob, PyPDF2, fnmatch

class FilesModule:
    def find_file(self, filename):
        """Searches for a file in common user directories."""
        try:
            search_dirs = [
                os.path.join(os.path.expanduser("~"), "Desktop"),
                os.path.join(os.path.expanduser("~"), "Documents"),
                os.path.join(os.path.expanduser("~"), "Downloads"),
                os.getcwd()
            ]

            matches = []
            pattern = f"*{filename}*"

            for root_dir in search_dirs:
                if not os.path.exists(root_dir): continue
                for root, dirnames, filenames in os.walk(root_dir):
                    for name in fnmatch.filter(filenames, pattern):
                        matches.append(os.path.join(root, name))
                    if len(matches) > 5: break # Limit results
                if matches: break

            if matches:
                res = "\n".join(matches[:3])
                return f"Located matches:\n{res}"
            return f"No archive matching '{filename}' found in tactical sectors."
        except Exception as e:
            return f"Search failed: {e}"

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
