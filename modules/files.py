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
                content = "".join([p.extract_text() for p in reader.pages[:10]])
                return f"PDF ANALYZED: {os.path.basename(file_path)}\nCONTENT:\n{content[:1500]}..."
        except Exception as e: return f"Analysis failed: {e}"

    def analyze_found_file(self, filename):
        """Finds and summarizes a file's content."""
        search_res = self.find_file(filename)
        if "Located matches" in search_res:
            path = search_res.split("\n")[1].strip()
            if path.endswith(".pdf"):
                return self.read_pdf(path)
            elif path.endswith((".txt", ".md", ".py")):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return f"ARCHIVE SUMMARY: {os.path.basename(path)}\nDATA:\n{f.read(1500)}..."
                except: return "Failed to read data sector."
        return search_res

    @staticmethod
    def open_document(name):
        doc_path = os.path.join(os.path.expanduser("~"), "Documents")
        if not name or "documents" in name.lower():
            os.startfile(doc_path)
            return "Tactical data vault opened."

        matches = glob.glob(os.path.join(doc_path, f"*{name}*"))
        if matches:
            os.startfile(matches[0])
            return f"Opening archive: {os.path.basename(matches[0])}"
        return f"Archive '{name}' not found in tactical sectors."
