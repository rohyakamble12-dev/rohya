import os
import subprocess
import time
import shutil
import ctypes
from veda.utils.sanitizer import VedaSanitizer

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import pygetwindow as gw
    WINDOWS_MANAGEMENT = True
except ImportError:
    WINDOWS_MANAGEMENT = False

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER; from comtypes import CLSCTX_ALL
    WINDOWS_AUDIO = True
except ImportError:
    WINDOWS_AUDIO = False

try:
    import screen_brightness_control as sbc
    WINDOWS_BRIGHTNESS = True
except ImportError:
    WINDOWS_BRIGHTNESS = False

class SystemControl:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "open_app": self.open_app,
            "close_app": self.close_app,
            "set_volume": self.set_volume,
            "set_brightness": self.set_brightness,
            "lock_pc": self.lock_pc,
            "screenshot": self.screenshot,
            "find": self.find,
            "move": self.move,
            "list_windows": self.list_windows,
            "focus_window": self.focus_window,
            "power_off": self.shutdown,
            "restart": self.restart,
            "set_wallpaper": self.set_wallpaper,
            "notify": self.send_notification
        }

    def open_app(self, params):
        app_name = params.get("app_name", "")
        safe_app = VedaSanitizer.normalize_app_name(app_name)
        if not safe_app: return "Application name missing."

        # Strictly controlled whitelist to prevent unwanted launches
        allowed_apps = {
            "chrome": ["start", "chrome"],
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "settings": ["start", "ms-settings:display"],
            "explorer": ["explorer.exe"],
            "paint": ["mspaint.exe"],
            "cmd": ["start", "cmd.exe"],
            "powershell": ["start", "powershell.exe"],
            "taskmgr": ["taskmgr.exe"]
        }

        if safe_app.lower() in allowed_apps:
            args = allowed_apps[safe_app.lower()]
            subprocess.Popen(args, shell=True)
            return f"Opening {safe_app}"
        else:
            # For non-whitelisted apps, we attempt a search rather than direct execution
            # this prevents the 'code' or other accidental triggers
            return f"Application '{safe_app}' is not in my tactical whitelist. Would you like me to search for it?"

    def close_app(self, params):
        app_name = params.get("app_name", "")
        safe_app = VedaSanitizer.normalize_app_name(app_name)
        subprocess.run(["taskkill", "/f", "/im", f"{safe_app}.exe"], check=False, capture_output=True)
        return f"Closing {safe_app}"

    def set_volume(self, params):
        if not WINDOWS_AUDIO: return "Audio control unavailable."
        level = params.get("level", 50)
        try:
            volume = cast(AudioUtilities.GetSpeakers().Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None), POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(float(level) / 100, None)
            return f"Volume set to {level}%"
        except Exception as e: return f"Volume adjustment failed: {e}"

    def set_brightness(self, params):
        if not WINDOWS_BRIGHTNESS: return "Brightness control unavailable."
        level = params.get("level", 50)
        try:
            sbc.set_brightness(int(level))
            return f"Brightness optimized to {level}%"
        except Exception as e: return f"Brightness adjustment failed: {e}"

    def lock_pc(self, params=None):
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        return "Tactical lock engaged. OS secured."

    def shutdown(self, params=None):
        os.system("shutdown /s /t 60")
        return "System shutdown initiated. 60 seconds to termination."

    def restart(self, params=None):
        os.system("shutdown /r /t 60")
        return "System restart initiated. Standby for reboot."

    def set_wallpaper(self, params):
        path = params.get("path")
        if not path or not os.path.exists(path): return "Invalid image path."
        try:
            # SPI_SETDESKWALLPAPER = 20
            ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(path), 0)
            return "Tactical wallpaper updated."
        except Exception as e: return f"Wallpaper update failed: {e}"

    def send_notification(self, params):
        msg = params.get("message", "Tactical Update")
        title = params.get("title", "VEDA")
        try:
            # Fallback PowerShell notification
            fallback_cmd = f'powershell -Command "[Reflection.Assembly]::LoadWithPartialName(\'System.Windows.Forms\'); [System.Windows.Forms.MessageBox]::Show(\'{msg}\', \'{title}\')"'
            subprocess.run(fallback_cmd, shell=True)
            return "Notification dispatched."
        except: return "Notification link failed."

    def screenshot(self, params=None):
        if not PYAUTOGUI_AVAILABLE:
            return "Screenshot capability offline: pyautogui not installed."
        try:
            pic_dir = os.path.join(os.path.expanduser("~"), "Pictures")
            if not os.path.exists(pic_dir): os.makedirs(pic_dir)
            path = os.path.join(pic_dir, f"Veda_Capture_{int(time.time())}.png")
            pyautogui.screenshot(path)
            return f"Screenshot saved to {path}."
        except Exception as e: return f"Capture failed: {e}"

    def find(self, params):
        query = params.get("query", "")
        if not query: return "Search query missing."
        user_home = os.path.expanduser("~")
        results = []
        target_folders = ["Documents", "Desktop", "Downloads", "Pictures"]
        for folder in target_folders:
            path = os.path.join(user_home, folder)
            if not os.path.exists(path): continue
            for root, _, files in os.walk(path):
                depth = root[len(path):].count(os.sep)
                if depth > 1: continue
                for f in files:
                    if query.lower() in f.lower():
                        results.append(os.path.join(root, f))
                    if len(results) >= 5: break
                if len(results) >= 5: break
            if len(results) >= 5: break

        if results:
            res_str = "\n".join(results[:3])
            if len(results) > 3: res_str += f"\n... and {len(results)-3} more."
            return f"Matches found:\n{res_str}"
        return f"No matches found for '{query}'."

    def move(self, params):
        src, dst = params.get("source"), params.get("destination")
        if not src or not dst: return "Source or destination parameters missing."
        try:
            if os.path.exists(src):
                shutil.move(src, dst)
                return f"Successfully moved {src} to {dst}."
            return f"Source path '{src}' does not exist."
        except Exception as e: return f"Relocation failed: {e}"

    def list_windows(self, params=None):
        if not WINDOWS_MANAGEMENT: return "Window management link broken."
        windows = gw.getAllTitles()
        active = [w for w in windows if w.strip()]
        return "Active Windows:\n" + "\n".join(active[:10])

    def focus_window(self, params):
        if not WINDOWS_MANAGEMENT: return "Window management link broken."
        title = params.get("title", "")
        try:
            win = gw.getWindowsWithTitle(title)[0]
            win.activate()
            return f"Interface focus shifted to {title}."
        except: return f"Target window '{title}' not found."
