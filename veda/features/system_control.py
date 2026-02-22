import os
import subprocess
import pyautogui
import webbrowser
import re
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import screen_brightness_control as sbc
from veda.features.base import VedaPlugin, PermissionTier

class SystemPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
        self.register_intent("open_app", self.open_app, PermissionTier.SAFE)
        self.register_intent("close_app", self.close_app, PermissionTier.CONFIRM_REQUIRED)
        self.register_intent("set_volume", self.set_volume, PermissionTier.SAFE)
        self.register_intent("set_brightness", self.set_brightness, PermissionTier.SAFE)
        self.register_intent("lock_pc", self.lock_pc, PermissionTier.SAFE)
        self.register_intent("sleep", self.system_sleep, PermissionTier.CONFIRM_REQUIRED)
        self.register_intent("mute_toggle", self.toggle_mute, PermissionTier.SAFE)
        self.register_intent("screenshot", self.screenshot, PermissionTier.SAFE)
        self.register_intent("web_find", self.web_find, PermissionTier.SAFE)
        self.register_intent("empty_trash", self.empty_recycle_bin, PermissionTier.CONFIRM_REQUIRED)
        self.register_intent("set_wallpaper", self.set_wallpaper, PermissionTier.SAFE)

    def _sanitize(self, text):
        return re.sub(r'[^a-zA-Z0-9\s._-]', '', str(text)).strip()

    WEB_FALLBACKS = {
        "word": "https://www.office.com/launch/word",
        "excel": "https://www.office.com/launch/excel",
        "powerpoint": "https://www.office.com/launch/powerpoint",
        "outlook": "https://outlook.live.com/",
        "discord": "https://discord.com/app",
        "spotify": "https://open.spotify.com/",
        "youtube": "https://www.youtube.com",
        "whatsapp": "https://web.whatsapp.com/",
        "telegram": "https://web.telegram.org/",
        "chrome": "https://www.google.com",
        "gmail": "https://mail.google.com/",
        "maps": "https://www.google.com/maps",
        "github": "https://github.com/",
        "netflix": "https://www.netflix.com/"
    }

    def open_app(self, params):
        app_name = self._sanitize(params.get("app_name", ""))
        if not app_name: return "Specify an application to open."

        app_name_lower = app_name.lower()
        apps = {
            "chrome": "chrome",
            "notepad": "notepad",
            "calculator": "calc",
            "settings": "ms-settings:",
            "explorer": "explorer",
            "task manager": "taskmgr",
            "cmd": "cmd",
            "powershell": "powershell"
        }

        target = apps.get(app_name_lower, app_name_lower)

        try:
            os.startfile(target)
            return f"Opening {app_name}."
        except Exception:
            try:
                subprocess.Popen(f"start {target}", shell=True)
                return f"Launching {app_name}."
            except Exception:
                if app_name_lower in self.WEB_FALLBACKS:
                    webbrowser.open(self.WEB_FALLBACKS[app_name_lower])
                    return f"Opening web version of {app_name}."

                webbrowser.open(f"https://www.google.com/search?q=open+{app_name}")
                return f"I couldn't find {app_name} locally. Searching for it..."

    def close_app(self, params):
        app_name = self._sanitize(params.get("app_name", ""))
        try:
            subprocess.run(["taskkill", "/f", "/im", f"{app_name}.exe"], capture_output=True)
            subprocess.run(["taskkill", "/f", "/im", app_name], capture_output=True)
            return f"Attempted to terminate {app_name}."
        except Exception as e:
            return f"Failed to close {app_name}: {str(e)}"

    def set_volume(self, params):
        level = params.get("level", 50)
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(float(level) / 100, None)
            return f"Volume set to {level}%."
        except Exception as e:
            return f"Volume control failed: {e}"

    def set_brightness(self, params):
        level = params.get("level", 50)
        try:
            sbc.set_brightness(int(level))
            return f"Brightness set to {level}%."
        except Exception:
            return "Screen brightness control not supported."

    def lock_pc(self, params):
        try:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "System locked."
        except Exception as e:
            return f"Lock failed: {e}"

    def system_sleep(self, params):
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Suspending system."
        except Exception as e:
            return f"Sleep command failed: {e}"

    def toggle_mute(self, params):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current_mute = volume.GetMute()
            volume.SetMute(not current_mute, None)
            state = "Muted" if not current_mute else "Unmuted"
            return f"System {state}."
        except Exception as e:
            return f"Mute toggle failed: {e}"

    def screenshot(self, params):
        try:
            save_path = os.path.join(os.path.expanduser("~"), "Pictures", "Veda_Screenshot.png")
            pyautogui.screenshot(save_path)
            return f"Screenshot saved to Pictures."
        except Exception as e:
            return f"Screenshot failed: {e}"

    def web_find(self, params):
        query = self._sanitize(params.get("query", "google"))
        try:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Searching for '{query}'."
        except Exception as e:
            return f"Search failed: {e}"

    def empty_recycle_bin(self, params):
        try:
            import winshell
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)
            return "Recycle bin purged."
        except Exception as e:
            return f"Purge failed: {e}"

    def set_wallpaper(self, params):
        import ctypes
        path = params.get("path", "")
        try:
            if not os.path.exists(path): return "Image not found."
            ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, path, 0x01 | 0x02)
            return "Wallpaper updated."
        except Exception as e:
            return f"Update failed: {e}"
