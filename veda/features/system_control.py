import os
import subprocess
import pyautogui
import webbrowser
import re
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import screen_brightness_control as sbc
import shutil

class SystemControl:
    @staticmethod
    def _sanitize(text):
        """Sanitizes input to prevent command injection."""
        return re.sub(r'[^a-zA-Z0-9\s._-]', '', text).strip()

    # Mapping of apps to web alternatives
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

    @staticmethod
    def open_app(app_name):
        """Opens an application locally, or falls back to a web version."""
        app_name = SystemControl._sanitize(app_name)
        app_name_lower = app_name.lower()

        # 1. Try common local command aliases with 'start'
        apps = {
            "chrome": "chrome",
            "notepad": "notepad",
            "calculator": "calc",
            "settings": "ms-settings:",
            "explorer": "explorer",
            "task manager": "taskmgr",
            "cmd": "cmd",
            "powershell": "powershell",
            "browser": "https://www.google.com"
        }

        target = apps.get(app_name_lower, app_name_lower)

        # 2. Attempt to use Windows 'start' command for maximum resilience
        try:
            # os.startfile is built into Python on Windows and very effective
            os.startfile(target)
            return f"Opening {app_name} via Windows Shell."
        except Exception:
            pass

        # 3. Try subprocess with shell=True as fallback
        try:
            subprocess.Popen(f"start {target}", shell=True)
            return f"Launching {app_name}."
        except Exception:
            pass

        # 4. Web Fallback
        if app_name_lower in SystemControl.WEB_FALLBACKS:
            url = SystemControl.WEB_FALLBACKS[app_name_lower]
            webbrowser.open(url)
            return f"I couldn't find {app_name} locally, so I'm opening the web version for you."

        # 5. Last resort: Search for the app on Google
        search_url = f"https://www.google.com/search?q=open+{app_name}"
        webbrowser.open(search_url)
        return f"I couldn't find {app_name} on this system. I've initiated a search to help you find it."

    @staticmethod
    def close_app(app_name):
        """Closes an application by name."""
        app_name = SystemControl._sanitize(app_name)
        try:
            # Using subprocess list for better safety than os.system
            subprocess.run(["taskkill", "/f", "/im", f"{app_name}.exe"], capture_output=True)
            subprocess.run(["taskkill", "/f", "/im", app_name], capture_output=True)
            return f"Attempted to terminate {app_name} processes."
        except Exception as e:
            return f"Failed to close {app_name}: {str(e)}"

    @staticmethod
    def set_volume(level):
        """Sets system volume (0-100)."""
        try:
            # First try Native Volume Control
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(float(level) / 100, None)
            return f"Volume set to {level} percent"
        except Exception:
            # Fallback to pyautogui media keys (vague but works)
            try:
                # If they ask for low volume, just mute or something?
                # Better to just log failure.
                return f"Could not set precise volume. Please use your keyboard shortcuts."
            except Exception as e:
                return f"Volume control failure: {str(e)}"

    @staticmethod
    def set_brightness(level):
        """Sets screen brightness (0-100)."""
        try:
            sbc.set_brightness(int(level))
            return f"Brightness set to {level} percent"
        except Exception:
            return "Screen brightness control is not supported on this monitor."

    @staticmethod
    def lock_pc():
        """Locks the Windows PC."""
        try:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Locking the PC"
        except Exception as e:
            return f"Failed to lock PC: {str(e)}"

    @staticmethod
    def system_sleep():
        """Puts the Windows PC to sleep."""
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Initiating system suspension."
        except Exception as e:
            return f"Sleep command failed: {str(e)}"

    @staticmethod
    def toggle_mute():
        """Mutes or unmutes the system volume."""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current_mute = volume.GetMute()
            volume.SetMute(not current_mute, None)
            state = "Muted" if not current_mute else "Unmuted"
            return f"System audio {state}."
        except Exception as e:
            return f"Mute toggle failed: {str(e)}"

    @staticmethod
    def screenshot():
        """Takes a screenshot and saves it."""
        try:
            save_path = os.path.join(os.path.expanduser("~"), "Pictures", "Veda_Screenshot.png")
            pyautogui.screenshot(save_path)
            return f"Screenshot captured and saved to your Pictures folder."
        except Exception as e:
            return f"Failed to take screenshot: {str(e)}"

    @staticmethod
    def web_find(query):
        """Opens a browser and searches for the query."""
        query = SystemControl._sanitize(query)
        search_url = f"https://www.google.com/search?q={query}"
        try:
            webbrowser.open(search_url)
            return f"Searching for '{query}' in your browser."
        except Exception as e:
            return f"Failed to initiate web search: {str(e)}"
