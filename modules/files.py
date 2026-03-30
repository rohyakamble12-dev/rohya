import os, glob, fnmatch
try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

class FilesModule:
    def find_file(self, filename):
        """Searches for a file in common user directories with deep scan."""
        try:
            user_home = os.path.expanduser("~")
            search_dirs = [
                os.path.join(user_home, "Desktop"),
                os.path.join(user_home, "Documents"),
                os.path.join(user_home, "Downloads"),
                os.path.join(user_home, "Videos"),
                os.path.join(user_home, "Pictures"),
                os.getcwd()
            ]

            matches = []
            pattern = f"*{filename}*"

            for root_dir in search_dirs:
                if not os.path.exists(root_dir): continue
                # Optimized shallow search first
                shallow = glob.glob(os.path.join(root_dir, pattern))
                if shallow: matches.extend(shallow)

                if not matches:
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
        if not HAS_PDF: return "PDF analysis sector offline."
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

    def find_duplicates(self, path=None):
        """Identifies duplicate files using MD5 hashing."""
        import hashlib
        try:
            path = path or os.path.join(os.path.expanduser("~"), "Documents")
            hashes = {}
            duplicates = []
            for root, dirs, files in os.walk(path):
                for f in files:
                    file_path = os.path.join(root, f)
                    try:
                        with open(file_path, "rb") as f_obj:
                            file_hash = hashlib.md5(f_obj.read()).hexdigest()
                        if file_hash in hashes:
                            duplicates.append(file_path)
                        else:
                            hashes[file_hash] = file_path
                    except: continue

            if not duplicates: return f"SECTOR ANALYSIS: {os.path.basename(path)} is optimized. No duplicates detected."
            return f"DUPLICATE DETECTION: {len(duplicates)} redundant files found in {os.path.basename(path)}.\nSample: {os.path.basename(duplicates[0])}"
        except: return "Duplicate analysis protocol failed."

    def organize_directory(self, path=None):
        """MCU Accurate 'Data Cleanup': Organizes files into categories."""
        import shutil
        try:
            path = path or os.path.join(os.path.expanduser("~"), "Downloads")
            if not os.path.exists(path): return "ORGANIZATION: Target sector not found."

            mapping = {
                "Documents": [".pdf", ".docx", ".txt", ".md", ".pptx", ".xlsx"],
                "Media": [".jpg", ".png", ".mp4", ".mp3", ".wav", ".mov"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "Scripts": [".py", ".js", ".sh", ".bat"]
            }

            moved = 0
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    ext = os.path.splitext(item)[1].lower()
                    for folder, extensions in mapping.items():
                        if ext in extensions:
                            dest_dir = os.path.join(path, folder)
                            os.makedirs(dest_dir, exist_ok=True)
                            shutil.move(item_path, os.path.join(dest_dir, item))
                            moved += 1
                            break

            return f"ORGANIZATION COMPLETE: {moved} files relocated into categorized sub-sectors in {os.path.basename(path)}."
        except Exception as e:
            return f"Organization protocol failed: {e}"
