import os
import fnmatch
import shutil
import hashlib
import zipfile
from datetime import datetime
from PIL import Image
from veda.features.base import VedaPlugin, PermissionTier
from veda.utils.sandbox import sandbox

class FilePlugin(VedaPlugin):
    def setup(self):
        # 1. Strict Contract Enforcement for Filesystem Operations
        path_schema = {"type": "string", "minLength": 1, "maxLength": 260}

        self.register_intent("file_search", self.search_file, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"filename": {"type": "string", "maxLength": 100}}, "required": ["filename"], "additionalProperties": False})

        self.register_intent("move_item", self.move_item, PermissionTier.SAFE, undo_method=self.undo_move,
                            input_schema={"type": "object", "properties": {"src": path_schema, "dst": path_schema}, "required": ["src", "dst"], "additionalProperties": False})

        self.register_intent("copy_item", self.copy_item, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"src": path_schema, "dst": path_schema}, "required": ["src", "dst"], "additionalProperties": False})

        self.register_intent("delete_item", self.delete_item, PermissionTier.CONFIRM_REQUIRED,
                            input_schema={"type": "object", "properties": {"path": path_schema, "secure": {"type": "boolean"}}, "required": ["path"], "additionalProperties": False})

        self.register_intent("convert_item", self.convert_image, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"src": path_schema, "target": {"enum": ["png", "jpg", "pdf"]}}, "required": ["src", "target"], "additionalProperties": False})

        self.register_intent("zip_item", self.zip_item, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"path": path_schema}, "required": ["path"], "additionalProperties": False})

        self.register_intent("unzip_item", self.unzip_item, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"path": path_schema}, "required": ["path"], "additionalProperties": False})

        self.register_intent("find_duplicates", self.find_duplicates, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})

        self.register_intent("find_large_files", self.find_large_files, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})

        self.register_intent("encrypt_item", self.encrypt_file, PermissionTier.CONFIRM_REQUIRED,
                            input_schema={"type": "object", "properties": {"path": path_schema, "key": {"type": "string", "minLength": 8, "maxLength": 100}}, "required": ["path"], "additionalProperties": False})

        self.register_intent("decrypt_item", self.decrypt_file, PermissionTier.CONFIRM_REQUIRED,
                            input_schema={"type": "object", "properties": {"path": path_schema, "key": {"type": "string", "maxLength": 100}}, "required": ["path"], "additionalProperties": False})

        self.register_intent("organize_dir", self.organize_directory, PermissionTier.CONFIRM_REQUIRED,
                            input_schema={"type": "object", "properties": {"directory": path_schema}, "required": ["directory"], "additionalProperties": False})

        self.register_intent("init_project", self.initialize_project, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"directory": path_schema, "type": {"type": "string"}}, "required": ["directory"], "additionalProperties": False})

        self.register_intent("folder_intel", self.summarize_directory, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"directory": path_schema}, "additionalProperties": False})

        self.register_intent("backup_item", self.backup_item, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"path": path_schema}, "required": ["path"], "additionalProperties": False})

        self.register_intent("file_info", self.get_file_info, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"path": path_schema}, "required": ["path"], "additionalProperties": False})

    def _get_authorized_base(self):
        """Zero-Trust: Restricting file operations to the user's profile sectors."""
        return os.path.abspath(os.path.expanduser("~"))

    def validate_params(self, intent, params):
        # 1. Mandatory Path Sandboxing
        paths_to_check = ['path', 'src', 'dst', 'directory']
        for key in paths_to_check:
            if key in params and params[key]:
                # Force path into the user profile 'jail'
                sanitized = sandbox.sanitize_path(params[key], base_dirs=[self._get_authorized_base()])
                if not sanitized:
                    return False, f"Sector Violation: Path '{params[key]}' is outside authorized tactical zones."
                params[key] = sanitized
        return True, "Valid."

    def predict_impact(self, intent, params):
        if intent == "delete_item":
            return f"Impact: Permanent removal of file/folder at sector {os.path.basename(params.get('path', ''))}."
        return super().predict_impact(intent, params)

    def get_best_match(self, filename):
        search_path = self._get_authorized_base()
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
        # Use sanitized base path
        search_path = self._get_authorized_base()
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
                if len(matches) >= 5: break
            if len(matches) >= 5: break
        if not matches: return "No matches found in authorized sectors."
        return "Matches found:\n" + "\n".join(matches)

    def move_item(self, params):
        src = params.get("src", "")
        dst = params.get("dst", "")

        # Absolute path validation (double check even after governance)
        src = sandbox.sanitize_path(src, [self._get_authorized_base()])
        dst = sandbox.sanitize_path(dst, [self._get_authorized_base()])

        if not src or not dst: return "Security Violation: Source or destination path restricted."

        if not os.path.exists(src):
            resolved = self.get_best_match(src)
            if resolved: src = resolved
            else: return f"Source {src} not found."

        # Track for undo
        params["_actual_src"] = src
        params["_actual_dst"] = os.path.join(dst, os.path.basename(src)) if os.path.isdir(dst) else dst

        try:
            shutil.move(src, dst)
            return f"Successfully relocated item to {dst}."
        except Exception as e:
            return f"Relocation failed: {e}"

    def undo_move(self, params):
        try:
            shutil.move(params["_actual_dst"], params["_actual_src"])
            return "Sequence reversed."
        except Exception as e: return "Rollback protocol failure."

    def delete_item(self, params):
        path = sandbox.sanitize_path(params.get("path", ""), [self._get_authorized_base()])
        if not path: return "Security Violation: Target path restricted."

        secure = params.get("secure", False)
        if not os.path.exists(path):
            return "Target path not found."
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
            return f"Sector purged: {os.path.basename(path)}."
        except Exception as e:
            return f"Purge failed: {e}"

    def encrypt_file(self, params):
        """Harden: AES-GCM for file encryption instead of ECB."""
        path = sandbox.sanitize_path(params.get("path", ""), [self._get_authorized_base()])
        if not path: return "Security Violation: Path restricted."

        key = params.get("key", "StarkIndustrialSecret")
        try:
            from Crypto.Cipher import AES
            import base64
            # Key derivation
            hashed_key = hashlib.sha256(key.encode()).digest()
            cipher = AES.new(hashed_key, AES.MODE_GCM)
            with open(path, 'rb') as f: data = f.read()
            ciphertext, tag = cipher.encrypt_and_digest(data)

            # Store nonce + tag + ciphertext
            with open(path + ".enc", 'wb') as f:
                f.write(cipher.nonce)
                f.write(tag)
                f.write(ciphertext)
            return f"Encryption complete: {os.path.basename(path)}.enc (Authenticated)"
        except Exception as e:
            return f"Encryption protocol failure: {e}"

    def decrypt_file(self, params):
        """Harden: AES-GCM Decryption."""
        path = sandbox.sanitize_path(params.get("path", ""), [self._get_authorized_base()])
        if not path: return "Security Violation: Path restricted."

        key = params.get("key", "StarkIndustrialSecret")
        if not path.endswith(".enc"): return "Invalid encrypted signature."
        try:
            from Crypto.Cipher import AES
            hashed_key = hashlib.sha256(key.encode()).digest()
            with open(path, 'rb') as f:
                nonce = f.read(16) # GCM default nonce is 16 for some impl, but 12 is standard.
                # Wait, pycryptodome default GCM nonce length is 16 if not specified,
                # but better to be explicit.
                tag = f.read(16)
                ciphertext = f.read()

            cipher = AES.new(hashed_key, AES.MODE_GCM, nonce=nonce)
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)

            output_path = path[:-4]
            with open(output_path, 'wb') as f: f.write(decrypted_data)
            return f"Decryption complete: {os.path.basename(output_path)}"
        except Exception as e:
            return f"Decryption protocol failure: {e}"

    def summarize_directory(self, params):
        directory = sandbox.sanitize_path(params.get("directory") or os.getcwd(), [self._get_authorized_base()])
        if not directory: return "Security Violation: Directory restricted."
        try:
            files = os.listdir(directory)
            return f"Sector {os.path.basename(directory)} contains {len(files)} items."
        except Exception as e:
            return f"Summarization failed: {e}"

    def initialize_project(self, params):
        directory = sandbox.sanitize_path(params.get("directory", "NewProject"), [self._get_authorized_base()])
        if not directory: return "Security Violation: Directory restricted."

        p_type = params.get("type", "code")
        try:
            os.makedirs(directory, exist_ok=True)
            return f"Tactical architecture '{p_type}' initialized in {directory}."
        except Exception as e: return f"Init failed: {e}"

    def organize_directory(self, params):
        directory = params.get("directory")
        if not directory or not os.path.exists(directory): return "Target sector missing."

        mapping = {
            "Images": [".jpg", ".png", ".gif", ".bmp"],
            "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
            "Archives": [".zip", ".rar", ".7z"],
            "Media": [".mp3", ".mp4", ".wav"]
        }

        for f in os.listdir(directory):
            p = os.path.join(directory, f)
            if os.path.isfile(p):
                ext = os.path.splitext(f)[1].lower()
                for folder, exts in mapping.items():
                    if ext in exts:
                        dest = os.path.join(directory, folder)
                        os.makedirs(dest, exist_ok=True)
                        shutil.move(p, dest)
                        break
        return f"Sector {os.path.basename(directory)} organized by file classification."

    def backup_item(self, params):
        path = sandbox.sanitize_path(params.get("path", ""), [self._get_authorized_base()])
        if not path: return "Security Violation: Path restricted."
        try:
            dst = path + "_backup_" + datetime.now().strftime("%Y%m%d%H%M%S")
            if os.path.isdir(path): shutil.copytree(path, dst)
            else: shutil.copy2(path, dst)
            return f"Backup secured at {dst}."
        except Exception as e: return f"Backup protocol failure: {e}"

    def get_file_info(self, params):
        path = sandbox.sanitize_path(params.get("path", ""), [self._get_authorized_base()])
        if not path: return "Security Violation: Path restricted."
        try:
            stats = os.stat(path)
            return f"Intel: {os.path.basename(path)}, Size: {stats.st_size} bytes."
        except Exception as e: return f"Intel retrieval failed: {e}"

    def copy_item(self, params):
        src = sandbox.sanitize_path(params.get("src", ""), [self._get_authorized_base()])
        dst = sandbox.sanitize_path(params.get("dst", ""), [self._get_authorized_base()])
        if not src or not dst: return "Security Violation: Path restricted."
        try:
            if os.path.isdir(src): shutil.copytree(src, dst)
            else: shutil.copy2(src, dst)
            return f"Item duplicated to {dst}."
        except Exception as e: return f"Duplication failed: {e}"

    def convert_image(self, params):
        src = sandbox.sanitize_path(params.get("src", ""), [self._get_authorized_base()])
        if not src: return "Security Violation: Path restricted."
        target = params.get("target", "png")
        try:
            with Image.open(src) as img:
                out = os.path.splitext(src)[0] + "." + target
                img.save(out)
                return f"Visualization converted to {target}."
        except Exception as e: return f"Conversion failure: {e}"

    def zip_item(self, params):
        path = sandbox.sanitize_path(params.get("path", ""), [self._get_authorized_base()])
        if not path: return "Security Violation: Path restricted."
        try:
            shutil.make_archive(path, 'zip', path)
            return f"Archive secured: {path}.zip"
        except Exception as e: return f"Archiving failed: {e}"

    def unzip_item(self, params):
        path = sandbox.sanitize_path(params.get("path", ""), [self._get_authorized_base()])
        if not path: return "Security Violation: Path restricted."
        try:
            with zipfile.ZipFile(path, 'r') as z:
                z.extractall(os.path.splitext(path)[0])
            return f"Archive extracted."
        except Exception as e: return f"Extraction failed: {e}"

    def find_duplicates(self, params):
        base = self._get_authorized_base()
        hashes = {}
        duplicates = []
        for root, _, files in os.walk(base):
            for f in files:
                p = os.path.join(root, f)
                try:
                    if os.path.getsize(p) > 1024*1024*100: continue # Skip huge files
                    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
                    if h in hashes: duplicates.append(p)
                    else: hashes[h] = p
                except: continue
            if len(duplicates) > 10: break

        if not duplicates: return "No redundancies detected in primary sectors."
        return "Potential duplicates found:\n" + "\n".join(duplicates[:5])

    def find_large_files(self, params):
        base = self._get_authorized_base()
        large = []
        for root, _, files in os.walk(base):
            for f in files:
                p = os.path.join(root, f)
                try:
                    s = os.path.getsize(p)
                    if s > 1024*1024*500: # 500MB
                        large.append((p, s))
                except: continue
        large.sort(key=lambda x: x[1], reverse=True)
        if not large: return "Storage audit: No oversized files detected."
        return "Large files detected:\n" + "\n".join([f"{x[0]} ({x[1]//1024**2}MB)" for x in large[:5]])
