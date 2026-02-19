import os
import fnmatch

class VedaFileManager:
    @staticmethod
    def search_file(filename, search_path=None):
        """Searches for a file by name (with wildcards) in user directories."""
        if search_path is None:
            # Default to User profile
            search_path = os.path.expanduser("~")

        matches = []
        # Limit search to avoid long hangs - top level folders
        important_dirs = ['Documents', 'Downloads', 'Desktop', 'Pictures', 'Videos']

        for folder in important_dirs:
            full_path = os.path.join(search_path, folder)
            if not os.path.exists(full_path):
                continue

            for root, dirnames, filenames in os.walk(full_path):
                for f in fnmatch.filter(filenames, f"*{filename}*"):
                    matches.append(os.path.join(root, f))
                    if len(matches) >= 5: # Limit results
                        break
                if len(matches) >= 5:
                    break

        if not matches:
            return "I couldn't find any files matching that description in your primary folders."

        result_str = "I found the following matches:\n" + "\n".join(matches)
        return result_str

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
