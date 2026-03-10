import os
import subprocess
import pyautogui
import threading
import time
from veda.utils.sanitizer import VedaSanitizer

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    WINDOWS_AUDIO = True
except ImportError:
    WINDOWS_AUDIO = False

try:
    import screen_brightness_control as sbc
    WINDOWS_BRIGHTNESS = True
except ImportError:
    WINDOWS_BRIGHTNESS = False

class SystemControl:
    @staticmethod
    def open_app(app_name):
        """Opens an application by name safely."""
        try:
            # Strictly sanitize the app name to prevent command injection
            safe_app = VedaSanitizer.normalize_app_name(app_name)
            if not safe_app:
                return "I couldn't identify the application you want to open."

            # Basic common apps mapping
            apps = {
                "chrome": ["start", "chrome"],
                "notepad": ["notepad.exe"],
                "calculator": ["calc.exe"],
                "settings": ["start", "ms-settings:"],
                "explorer": ["explorer.exe"],
                "paint": ["mspaint.exe"],
                "cmd": ["start", "cmd.exe"],
                "powershell": ["start", "powershell.exe"]
            }

            args = apps.get(safe_app.lower(), ["start", safe_app])
            # Use shell=True for 'start' commands on Windows, but since we sanitized, it's safer
            # Note: subprocess.Popen is generally better than os.system to avoid blocking
            subprocess.Popen(args, shell=True)
            return f"Opening {safe_app}"
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"

    @staticmethod
    def close_app(app_name):
        """Closes an application by name safely."""
        try:
            safe_app = VedaSanitizer.normalize_app_name(app_name)
            # Common app name normalization for taskkill
            app_map = {
                "chrome": "chrome",
                "notepad": "notepad",
                "calculator": "CalculatorApp",
                "paint": "mspaint",
                "explorer": "explorer"
            }
            im_name = app_map.get(safe_app.lower(), safe_app)
            # Use taskkill safely
            subprocess.run(["taskkill", "/f", "/im", f"{im_name}.exe"], check=False, capture_output=True)
            return f"Closing {safe_app}"
        except Exception as e:
            return f"Failed to close {app_name}: {str(e)}"

    @staticmethod
    def set_volume(level):
        """Sets system volume (0-100)."""
        if not WINDOWS_AUDIO:
            return "Volume control is only available on Windows."
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(float(level) / 100, None)
            return f"Volume set to {level} percent"
        except Exception as e:
            return f"Failed to set volume: {str(e)}"

    @staticmethod
    def set_brightness(level):
        """Sets screen brightness (0-100)."""
        if not WINDOWS_BRIGHTNESS:
            return "Brightness control is only available on Windows."
        try:
            sbc.set_brightness(int(level))
            return f"Brightness set to {level} percent"
        except Exception as e:
            return f"Failed to set brightness: {str(e)}"

    @staticmethod
    def lock_pc():
        """Locks the Windows PC."""
        try:
            # Using rundll32.exe safely
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
            return "Locking the PC"
        except Exception as e:
            return f"Failed to lock PC: {str(e)}"

    @staticmethod
    def screenshot():
        """Takes a screenshot and saves it."""
        try:
            pic_dir = os.path.join(os.path.expanduser("~"), "Pictures")
            if not os.path.exists(pic_dir):
                os.makedirs(pic_dir)
            path = os.path.join(pic_dir, f"Veda_Screenshot_{int(time.time())}.png")
            pyautogui.screenshot(path)
            return f"Screenshot saved to Pictures folder"
        except Exception as e:
            return f"Failed to take screenshot: {str(e)}"

    @staticmethod
    def find(query):
        """Searches for files in the current user's folder (limited depth)."""
        try:
            user_home = os.path.expanduser("~")
            results = []
            target_dirs = ["Documents", "Desktop", "Downloads", "Pictures"]
            for folder in target_dirs:
                path = os.path.join(user_home, folder)
                if not os.path.exists(path):
                    continue
                # Limit search depth to 2 to avoid GUI hang
                for root, dirs, files in os.walk(path):
                    depth = root[len(path):].count(os.sep)
                    if depth > 2:
                        continue
                    for file in files:
                        if query.lower() in file.lower():
                            results.append(os.path.join(root, file))
                        if len(results) >= 5: break
                    if len(results) >= 5: break
                if len(results) >= 5: break

            if results:
                res_str = "\n".join(results[:3])
                if len(results) > 3:
                    res_str += f"\n... and {len(results)-3} more."
                return f"I found these files:\n{res_str}"
            return f"I couldn't find any files matching '{query}'."
        except Exception as e:
            return f"Search failed: {str(e)}"

    @staticmethod
    def move(source, destination=None):
        """Moves a file or folder safely."""
        if not destination:
             return "Please specify both the file you want to move and the destination."
        try:
            import shutil
            # Ensure path safety
            if not os.path.exists(source):
                return f"Source file '{source}' does not exist."
            shutil.move(source, destination)
            return f"Moved '{source}' to '{destination}'"
        except Exception as e:
            return f"Failed to move: {str(e)}"
