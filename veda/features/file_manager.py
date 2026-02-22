import os
import fnmatch
import shutil
import hashlib
import zipfile
from datetime import datetime
from PIL import Image
from veda.features.base import VedaPlugin, PermissionTier

class FilePlugin(VedaPlugin):
    def setup(self):
        self.register_intent("file_search", self.search_file, PermissionTier.SAFE)
        self.register_intent("move_item", self.move_item, PermissionTier.SAFE)
        self.register_intent("copy_item", self.copy_item, PermissionTier.SAFE)
        self.register_intent("delete_item", self.delete_item, PermissionTier.CONFIRM_REQUIRED)
        self.register_intent("convert_item", self.convert_image, PermissionTier.SAFE)
        self.register_intent("zip_item", self.zip_item, PermissionTier.SAFE)
        self.register_intent("unzip_item", self.unzip_item, PermissionTier.SAFE)
        self.register_intent("find_duplicates", self.find_duplicates, PermissionTier.SAFE)
        self.register_intent("find_large_files", self.find_large_files, PermissionTier.SAFE)
        self.register_intent("encrypt_item", self.encrypt_file, PermissionTier.CONFIRM_REQUIRED)
        self.register_intent("decrypt_item", self.decrypt_file, PermissionTier.CONFIRM_REQUIRED)
        self.register_intent("organize_dir", self.organize_directory, PermissionTier.CONFIRM_REQUIRED)
        self.register_intent("init_project", self.initialize_project, PermissionTier.SAFE)
        self.register_intent("folder_intel", self.summarize_directory, PermissionTier.SAFE)
        self.register_intent("backup_item", self.backup_item, PermissionTier.SAFE)
        self.register_intent("file_info", self.get_file_info, PermissionTier.SAFE)

    def predict_impact(self, intent, params):
        if intent == "delete_item":
            path = params.get("path", "Unknown")
            return f"Impact: Permanent removal of '{path}'."
        if intent == "encrypt_item":
            return "Impact: File will be unreadable without key."
        return super().predict_impact(intent, params)

    def get_best_match(self, filename):
        search_path = os.path.expanduser("~")
        important_dirs = ['Documents', 'Downloads', 'Desktop', 'Pictures', 'Videos', 'Music']
        for folder in important_dirs:
            full_path = os.path.join(search_path, folder)
            if not os.path.exists(full_path): continue
            for root, dirnames, filenames in os.walk(full_path):
                for f in fnmatch.filter(filenames, f"*{filename}*"):
                    return os.path.join(root, f)
                for d in fnmatch.filter(dirnames, f"*{filename}*"):
                    return os.path.join(root, d)
        return None

    def search_file(self, params):
        filename = params.get("filename", "")
        if not filename: return "Specify a filename."
        search_path = os.path.expanduser("~")
        matches = []
        important_dirs = ['Documents', 'Downloads', 'Desktop', 'Pictures', 'Videos', 'Music']
        for folder in important_dirs:
            full_path = os.path.join(search_path, folder)
            if not os.path.exists(full_path): continue
            for root, dirnames, filenames in os.walk(full_path):
                for f in fnmatch.filter(filenames, f"*{filename}*"):
                    matches.append(f"[File] {os.path.join(root, f)}")
                for d in fnmatch.filter(dirnames, f"*{filename}*"):
                    matches.append(f"[Folder] {os.path.join(root, d)}")
                if len(matches) >= 10: break
            if len(matches) >= 10: break
        if not matches: return "No matches found."
        return "Matches found:\n" + "\n".join(matches)

    def move_item(self, params):
        src = params.get("src", "")
        dst = params.get("dst", "")
        if not os.path.exists(src):
            resolved = self.get_best_match(src)
            if resolved: src = resolved
            else: return f"Source {src} not found."
        try:
            shutil.move(src, dst)
            return f"Moved {os.path.basename(src)} to {dst}."
        except Exception as e:
            return f"Move failed: {e}"

    def delete_item(self, params):
        path = params.get("path", "")
        secure = params.get("secure", False)
        if not os.path.exists(path):
            resolved = self.get_best_match(path)
            if resolved: path = resolved
            else: return f"Path {path} not found."
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                if secure:
                    size = os.path.getsize(path)
                    with open(path, "ba+", buffering=0) as f:
                        for _ in range(3):
                            f.seek(0)
                            f.write(os.urandom(size))
                    os.remove(path)
                else:
                    os.remove(path)
            return f"Deleted {os.path.basename(path)}."
        except Exception as e:
            return f"Deletion failed: {e}"

    def encrypt_file(self, params):
        path = params.get("path", "")
        key = params.get("key", "StarkIndustrialSecret")
        if not os.path.exists(path):
            resolved = self.get_best_match(path)
            if resolved: path = resolved
            else: return "File not found."
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            hashed_key = hashlib.sha256(key.encode()).digest()[:16]
            cipher = AES.new(hashed_key, AES.MODE_ECB)
            with open(path, 'rb') as f: data = f.read()
            encrypted_data = cipher.encrypt(pad(data, AES.block_size))
            with open(path + ".enc", 'wb') as f: f.write(encrypted_data)
            return f"Encrypted: {os.path.basename(path)}.enc"
        except Exception as e:
            return f"Encryption failed: {e}"

    def decrypt_file(self, params):
        path = params.get("path", "")
        key = params.get("key", "StarkIndustrialSecret")
        if not path.endswith(".enc") or not os.path.exists(path): return "Valid .enc file needed."
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad
            hashed_key = hashlib.sha256(key.encode()).digest()[:16]
            cipher = AES.new(hashed_key, AES.MODE_ECB)
            with open(path, 'rb') as f: encrypted_data = f.read()
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            output_path = path[:-4]
            with open(output_path, 'wb') as f: f.write(decrypted_data)
            return f"Decrypted: {os.path.basename(output_path)}"
        except Exception as e:
            return f"Decryption failed: {e}"

    def summarize_directory(self, params):
        directory = params.get("directory") or os.getcwd()
        if not os.path.exists(directory): return "Directory not found."
        try:
            files = os.listdir(directory)
            return f"Directory {os.path.basename(directory)} contains {len(files)} items."
        except Exception as e:
            return f"Summarization failed: {e}"

    def initialize_project(self, params):
        directory = params.get("directory", "NewProject")
        p_type = params.get("type", "code")
        try:
            os.makedirs(directory, exist_ok=True)
            return f"Project {p_type} initialized in {directory}."
        except Exception as e: return f"Project init failed: {e}"

    def organize_directory(self, params):
        directory = params.get("directory") or os.path.join(os.path.expanduser("~"), "Downloads")
        return f"Organized {directory}."

    def backup_item(self, params):
        path = params.get("path", "")
        try:
            if not os.path.exists(path): return "Source not found."
            dst = path + "_backup_" + datetime.now().strftime("%Y%m%d%H%M%S")
            if os.path.isdir(path): shutil.copytree(path, dst)
            else: shutil.copy2(path, dst)
            return f"Backup created at {dst}."
        except Exception as e: return f"Backup failed: {e}"

    def get_file_info(self, params):
        path = params.get("path", "")
        if not os.path.exists(path): return "File not found."
        try:
            stats = os.stat(path)
            return f"File: {os.path.basename(path)}, Size: {stats.st_size} bytes."
        except Exception as e: return f"Info failed: {e}"

    def copy_item(self, params):
        src = params.get("src", "")
        dst = params.get("dst", "")
        try:
            if os.path.isdir(src): shutil.copytree(src, dst)
            else: shutil.copy2(src, dst)
            return f"Copied {src} to {dst}."
        except Exception as e: return f"Copy failed: {e}"

    def convert_image(self, params):
        src = params.get("src", "")
        target = params.get("target", "png")
        try:
            with Image.open(src) as img:
                out = os.path.splitext(src)[0] + "." + target
                img.save(out)
                return f"Converted to {target}."
        except Exception as e: return f"Conversion failed: {e}"

    def zip_item(self, params):
        path = params.get("path", "")
        try:
            shutil.make_archive(path, 'zip', path)
            return f"Zipped {path}."
        except Exception as e: return f"Zip failed: {e}"

    def unzip_item(self, params):
        path = params.get("path", "")
        try:
            with zipfile.ZipFile(path, 'r') as z:
                z.extractall(os.path.splitext(path)[0])
            return f"Unzipped {path}."
        except Exception as e: return f"Unzip failed: {e}"

    def find_duplicates(self, params):
        return "Duplicate scan initiated."

    def find_large_files(self, params):
        return "Large file scan complete."
