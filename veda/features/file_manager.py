import os
import fnmatch
import shutil
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
    def delete_item(path):
        """Deletes a file or folder."""
        try:
            if not os.path.exists(path):
                return f"Item '{path}' not found."

            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return f"Permanently deleted '{os.path.basename(path)}'."
        except Exception as e:
            return f"Deletion failed: {str(e)}"

    @staticmethod
    def convert_image(src, target_ext):
        """Converts an image file to another format (e.g., png to jpg)."""
        try:
            if not os.path.exists(src):
                return f"Image '{src}' not found."

            target_ext = target_ext.lower().replace('.', '')
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
    def get_file_info(file_path):
        """Returns details about a specific file."""
        if not os.path.exists(file_path):
            return "That file path does not exist."

        try:
            stats = os.stat(file_path)
            size_mb = round(stats.st_size / (1024 * 1024), 2)
            return f"File Info for {os.path.basename(file_path)}:\n- Size: {size_mb} MB\n- Path: {file_path}"
        except Exception as e:
            return f"Error retrieving file info: {str(e)}"
