import os
import shutil
import hashlib

class FileProPlugin:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "organize_downloads": self.organize_downloads,
            "file_dedupe": self.deduplicate_folder
        }

    def organize_downloads(self, params=None):
        dl_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(dl_path): return "Downloads folder not found."

        mapping = {
            "Images": [".jpg", ".jpeg", ".png", ".gif"],
            "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
            "Archives": [".zip", ".rar", ".7z"],
            "Media": [".mp3", ".mp4", ".wav"]
        }

        count = 0
        for item in os.listdir(dl_path):
            item_path = os.path.join(dl_path, item)
            if os.path.isfile(item_path):
                ext = os.path.splitext(item)[1].lower()
                for folder, exts in mapping.items():
                    if ext in exts:
                        dest_dir = os.path.join(dl_path, folder)
                        os.makedirs(dest_dir, exist_ok=True)
                        shutil.move(item_path, os.path.join(dest_dir, item))
                        count += 1
                        break
        return f"Organized {count} files in Downloads."

    def deduplicate_folder(self, params):
        folder = params.get("path")
        if not folder or not os.path.exists(folder): return "Path invalid."

        hashes = {}
        duplicates = 0
        for root, _, files in os.walk(folder):
            for f in files:
                f_path = os.path.join(root, f)
                with open(f_path, 'rb') as fh:
                    h = hashlib.md5(fh.read()).hexdigest()
                if h in hashes:
                    os.remove(f_path)
                    duplicates += 1
                else:
                    hashes[h] = f_path
        return f"Removed {duplicates} duplicate files."
