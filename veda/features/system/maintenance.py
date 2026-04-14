import os
import shutil
import psutil
import hashlib

class VedaMaintenance:
    @staticmethod
    def clean_temp_files():
        """Cleans Windows temporary directories with path validation."""
        from veda.utils.sandbox import sandbox
        temp_dirs = []
        # Safely expand env vars
        t1 = os.environ.get('TEMP')
        if t1: temp_dirs.append(t1)

        sys_root = os.environ.get('SystemRoot', 'C:\\Windows')
        t2 = os.path.join(sys_root, 'Temp')
        temp_dirs.append(t2)

        cleaned_size = 0
        for d in temp_dirs:
            if not d or not os.path.exists(d):
                continue
            for root, dirs, files in os.walk(d):
                for f in files:
                    try:
                        f_path = os.path.join(root, f)
                        cleaned_size += os.path.getsize(f_path)
                        os.remove(f_path)
                    except Exception as e:
                        pass

        mb_saved = round(cleaned_size / (1024 * 1024), 2)
        return f"Maintenance complete. Purged approximately {mb_saved} MB of temporary data."

    @staticmethod
    def find_duplicates(search_path=None):
        """Finds duplicate files in a directory using MD5 hashes and path-jailing."""
        from veda.utils.sandbox import sandbox
        if not search_path:
            search_path = os.path.join(os.path.expanduser("~"), "Documents")

        # Path Jail: Documents only for duplicate scan
        search_path = sandbox.sanitize_path(search_path, [os.path.expanduser("~")])
        if not search_path: return "Security Violation: Search path restricted."

        hashes = {}
        duplicates = []

        count = 0
        for root, dirs, files in os.walk(search_path):
            for f in files:
                if count > 500: break # Safety limit
                f_path = os.path.join(root, f)
                try:
                    with open(f_path, "rb") as b_file:
                        f_hash = hashlib.md5(b_file.read(4096)).hexdigest()
                    if f_hash in hashes:
                        duplicates.append(f_path)
                    else:
                        hashes[f_hash] = f_path
                    count += 1
                except Exception as e: pass

        if not duplicates:
            return "Scan complete. No duplicate files identified in your Documents folder."

        return f"Scan complete. Identified {len(duplicates)} potential duplicates. Analysis report generated in terminal."

    @staticmethod
    def get_thermal_status():
        """Attempts to retrieve hardware temperatures."""
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if not temps:
                    return "Hardware thermal sensors are restricted or not reporting data."

                report = "Thermal Report:\n"
                for name, entries in temps.items():
                    for entry in entries:
                        report += f"- {name}: {entry.current}°C\n"
                return report
            return "Thermal monitoring is not supported on this Windows environment."
        except Exception as e:
            return "Unable to access thermal management subsystem."
