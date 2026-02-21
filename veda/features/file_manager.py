import os
import fnmatch
import shutil
import hashlib
import zipfile
from datetime import datetime
from PIL import Image

class VedaFileManager:
    @staticmethod
    def search_file(filename, search_path=None):
        """Searches for a file or folder by name in user directories."""
        if search_path is None:
            # Default to User profile
            search_path = os.path.expanduser("~")

        matches = []
        # Expanded directories for searching
        important_dirs = ['Documents', 'Downloads', 'Desktop', 'Pictures', 'Videos', 'Music']

        for folder in important_dirs:
            full_path = os.path.join(search_path, folder)
            if not os.path.exists(full_path):
                continue

            for root, dirnames, filenames in os.walk(full_path):
                # Search files
                for f in fnmatch.filter(filenames, f"*{filename}*"):
                    matches.append(f"[File] {os.path.join(root, f)}")
                    if len(matches) >= 10: break

                # Search directories
                for d in fnmatch.filter(dirnames, f"*{filename}*"):
                    matches.append(f"[Folder] {os.path.join(root, d)}")
                    if len(matches) >= 10: break

                if len(matches) >= 10: break

        if not matches:
            return "I couldn't find any files matching that description in your primary folders."

        result_str = "I found the following matches:\n" + "\n".join(matches)
        return result_str

    @staticmethod
    def get_best_match(filename):
        """Returns the raw path of the first match found."""
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

    @staticmethod
    def move_item(src, dst):
        """Moves a file or folder to a new location."""
        try:
            if not os.path.exists(src):
                return f"Source item '{src}' not found."

            # If dst is a folder name, resolve it
            if not os.path.isabs(dst) or not os.path.isdir(dst):
                search_dst = VedaFileManager.get_best_match(dst)
                if search_dst and os.path.isdir(search_dst):
                    dst = search_dst

            shutil.move(src, dst)
            return f"Successfully moved '{os.path.basename(src)}' to '{dst}'."
        except Exception as e:
            return f"Move failed: {str(e)}"

    @staticmethod
    def copy_item(src, dst):
        """Copies a file or folder to a new location."""
        try:
            if not os.path.exists(src):
                return f"Source item '{src}' not found."

            # Resolve destination
            if not os.path.isabs(dst) or not os.path.isdir(dst):
                search_dst = VedaFileManager.get_best_match(dst)
                if search_dst and os.path.isdir(search_dst):
                    dst = search_dst

            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(dst, os.path.basename(src)))
            else:
                shutil.copy2(src, dst)
            return f"Successfully copied '{os.path.basename(src)}' to '{dst}'."
        except Exception as e:
            return f"Copy failed: {str(e)}"

    @staticmethod
    def delete_item(path, secure=False):
        """Deletes a file or folder. If secure, overwrites data first."""
        try:
            if not os.path.exists(path):
                return f"Item '{path}' not found."

            name = os.path.basename(path)
            if os.path.isdir(path):
                if secure:
                    # Securely delete all files in dir
                    for root, dirs, files in os.walk(path, topdown=False):
                        for f in files:
                            VedaFileManager.secure_delete_file(os.path.join(root, f))
                        for d in dirs:
                            os.rmdir(os.path.join(root, d))
                    os.rmdir(path)
                else:
                    shutil.rmtree(path)
            else:
                if secure:
                    VedaFileManager.secure_delete_file(path)
                else:
                    os.remove(path)

            msg = "Securely shredded" if secure else "Permanently deleted"
            return f"{msg} '{name}'."
        except Exception as e:
            return f"Deletion failed: {str(e)}"

    @staticmethod
    def secure_delete_file(path):
        """Overwrites a file with random data before deleting it."""
        size = os.path.getsize(path)
        with open(path, "ba+", buffering=0) as f:
            for _ in range(3): # 3-pass overwrite
                f.seek(0)
                f.write(os.urandom(size))
        os.remove(path)

    @staticmethod
    def convert_image(src, target_ext):
        """Converts an image file to another format (e.g., png to jpg)."""
        try:
            if not os.path.exists(src):
                return f"Image '{src}' not found."

            target_ext = target_ext.lower().replace('.', '')

            # Special case: Image to PDF
            if target_ext == "pdf":
                output_path = f"{os.path.splitext(src)[0]}.pdf"
                with Image.open(src) as img:
                    img.convert("RGB").save(output_path)
                return f"Converted to PDF: {output_path}"

            base = os.path.splitext(src)[0]
            output_path = f"{base}.{target_ext}"

            with Image.open(src) as img:
                if target_ext in ["jpg", "jpeg"]:
                    img = img.convert("RGB")
                img.save(output_path)

            return f"Image converted and saved to: {output_path}"
        except Exception as e:
            return f"Conversion failed: {str(e)}"

    @staticmethod
    def zip_item(path):
        """Zips a file or folder."""
        try:
            if not os.path.exists(path):
                return f"Item '{path}' not found."

            output_filename = f"{path}.zip"
            if os.path.isdir(path):
                shutil.make_archive(path, 'zip', path)
            else:
                with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(path, os.path.basename(path))
            return f"Archive created successfully: {output_filename}"
        except Exception as e:
            return f"Archiving failed: {str(e)}"

    @staticmethod
    def unzip_item(zip_path, extract_to=None):
        """Unzips a .zip file."""
        try:
            if not os.path.exists(zip_path):
                return f"Zip file '{zip_path}' not found."

            if extract_to is None:
                extract_to = os.path.splitext(zip_path)[0]

            os.makedirs(extract_to, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            return f"Extracted to: {extract_to}"
        except Exception as e:
            return f"Extraction failed: {str(e)}"

    @staticmethod
    def find_duplicates(directory=None):
        """Finds duplicate files based on hash."""
        if directory is None:
            directory = os.path.join(os.path.expanduser("~"), "Documents")

        hashes = {}
        duplicates = []

        try:
            for root, dirs, files in os.walk(directory):
                for f in files:
                    path = os.path.join(root, f)
                    if os.path.getsize(path) > 50 * 1024 * 1024: continue # Skip large files for speed

                    with open(path, 'rb') as file_obj:
                        file_hash = hashlib.md5(file_obj.read()).hexdigest()

                    if file_hash in hashes:
                        duplicates.append((path, hashes[file_hash]))
                    else:
                        hashes[file_hash] = path

            if not duplicates:
                return "No duplicate files found in that directory."

            result = "Duplicate scan complete. Found:\n"
            for dup, orig in duplicates[:5]:
                result += f"- {os.path.basename(dup)} (Same as {os.path.basename(orig)})\n"
            return result
        except Exception as e:
            return f"Duplicate scan failed: {str(e)}"

    @staticmethod
    def find_large_files(directory=None):
        """Lists the largest files in a directory."""
        if directory is None:
            directory = os.path.expanduser("~")

        file_list = []
        try:
            for root, dirs, files in os.walk(directory):
                for f in files:
                    path = os.path.join(root, f)
                    try:
                        file_list.append((path, os.path.getsize(path)))
                    except: continue

            file_list.sort(key=lambda x: x[1], reverse=True)

            result = "Storage intelligence report - Top 5 Largest Files:\n"
            for path, size in file_list[:5]:
                size_mb = round(size / (1024 * 1024), 2)
                result += f"- {os.path.basename(path)} ({size_mb} MB)\n"
            return result
        except Exception as e:
            return f"Storage scan failed: {str(e)}"

    @staticmethod
    def batch_rename(directory, pattern, replacement):
        """Renames files in a directory replacing pattern with replacement."""
        try:
            if directory is None:
                directory = os.path.join(os.path.expanduser("~"), "Documents")

            if not os.path.exists(directory):
                return f"Directory '{directory}' not found."

            count = 0
            for f in os.listdir(directory):
                if pattern in f:
                    new_name = f.replace(pattern, replacement)
                    os.rename(os.path.join(directory, f), os.path.join(directory, new_name))
                    count += 1
            return f"Batch rename complete. Updated {count} files in {os.path.basename(directory)}."
        except Exception as e:
            return f"Batch rename failed: {str(e)}"

    @staticmethod
    def organize_directory(directory=None):
        """Organizes files in a directory by moving them into subfolders based on extension."""
        if directory is None:
            directory = os.path.join(os.path.expanduser("~"), "Downloads")

        if not os.path.exists(directory):
            return "Directory not found."

        mapping = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx', '.csv'],
            'Archives': ['.zip', '.tar', '.rar', '.7z', '.gz'],
            'Media': ['.mp3', '.wav', '.mp4', '.mkv', '.mov', '.avi'],
            'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.json']
        }

        count = 0
        try:
            for f in os.listdir(directory):
                path = os.path.join(directory, f)
                if os.path.isdir(path): continue

                ext = os.path.splitext(f)[1].lower()
                for folder, extensions in mapping.items():
                    if ext in extensions:
                        dest_folder = os.path.join(directory, folder)
                        os.makedirs(dest_folder, exist_ok=True)
                        shutil.move(path, os.path.join(dest_folder, f))
                        count += 1
                        break
            return f"Intelligence Protocol: Organization complete. Sorted {count} items into categories."
        except Exception as e:
            return f"Organization failed: {str(e)}"

    @staticmethod
    def search_content(query, directory=None):
        """Searches for a string within text-based files in a directory."""
        if directory is None:
            directory = os.path.join(os.path.expanduser("~"), "Documents")

        results = []
        try:
            for root, dirs, files in os.walk(directory):
                for f in files:
                    if f.endswith(('.txt', '.py', '.md', '.log', '.json')):
                        path = os.path.join(root, f)
                        try:
                            with open(path, 'r', encoding='utf-8', errors='ignore') as file_obj:
                                if query.lower() in file_obj.read().lower():
                                    results.append(path)
                        except: continue
                    if len(results) >= 5: break
                if len(results) >= 5: break

            if not results:
                return f"No matches for '{query}' found in file contents."

            return "Content matches found in:\n" + "\n".join([os.path.basename(r) for r in results])
        except Exception as e:
            return f"Content search failed: {str(e)}"

    @staticmethod
    def encrypt_file(path, key="StarkIndustrialSecret"):
        """Encrypts a file (simplified implementation for the assistant)."""
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            import base64

            if not os.path.exists(path): return "File not found."

            # Ensure key is 16 bytes
            hashed_key = hashlib.sha256(key.encode()).digest()[:16]
            cipher = AES.new(hashed_key, AES.MODE_ECB)

            with open(path, 'rb') as f:
                data = f.read()

            encrypted_data = cipher.encrypt(pad(data, AES.block_size))

            with open(path + ".enc", 'wb') as f:
                f.write(encrypted_data)

            return f"File encrypted and saved as: {os.path.basename(path)}.enc"
        except ImportError:
            return "Encryption module (pycryptodome) not installed."
        except Exception as e:
            return f"Encryption failed: {str(e)}"

    @staticmethod
    def decrypt_file(path, key="StarkIndustrialSecret"):
        """Decrypts a .enc file."""
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad

            if not path.endswith(".enc"): return "Target must be a .enc file."
            if not os.path.exists(path): return "File not found."

            hashed_key = hashlib.sha256(key.encode()).digest()[:16]
            cipher = AES.new(hashed_key, AES.MODE_ECB)

            with open(path, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

            output_path = path[:-4] # Remove .enc
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)

            return f"File decrypted and saved as: {os.path.basename(output_path)}"
        except Exception as e:
            return f"Decryption failed: {str(e)}"

    @staticmethod
    def get_file_info(file_path):
        """Returns details about a specific file including metadata."""
        if not os.path.exists(file_path):
            return "That file path does not exist."

        try:
            stats = os.stat(file_path)
            size_mb = round(stats.st_size / (1024 * 1024), 2)
            created = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')

            info = f"File Intelligence Report for {os.path.basename(file_path)}:\n"
            info += f"- Path: {file_path}\n"
            info += f"- Size: {size_mb} MB\n"
            info += f"- Created: {created}\n"

            # Image specific metadata
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                with Image.open(file_path) as img:
                    info += f"- Dimensions: {img.width}x{img.height}\n"
                    info += f"- Format: {img.format}\n"
                    info += f"- Mode: {img.mode}\n"

            return info
        except Exception as e:
            return f"Error retrieving file intelligence: {str(e)}"
