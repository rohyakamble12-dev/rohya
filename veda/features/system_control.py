import os
import subprocess
import pyautogui
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import screen_brightness_control as sbc

class SystemControl:
    @staticmethod
    def open_app(app_name):
        """Opens an application by name."""
        try:
            # Basic common apps
            apps = {
                "chrome": "start chrome",
                "notepad": "notepad",
                "calculator": "calc",
                "settings": "start ms-settings:",
                "explorer": "start explorer"
            }
            cmd = apps.get(app_name.lower(), f"start {app_name}")
            os.system(cmd)
            return f"Opening {app_name}"
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"

    @staticmethod
    def close_app(app_name):
        """Closes an application by name."""
        try:
            os.system(f"taskkill /f /im {app_name}.exe")
            return f"Closing {app_name}"
        except Exception as e:
            return f"Failed to close {app_name}: {str(e)}"

    @staticmethod
    def set_volume(level):
        """Sets system volume (0-100)."""
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
        try:
            sbc.set_brightness(int(level))
            return f"Brightness set to {level} percent"
        except Exception as e:
            return f"Failed to set brightness: {str(e)}"

    @staticmethod
    def lock_pc():
        """Locks the Windows PC."""
        try:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Locking the PC"
        except Exception as e:
            return f"Failed to lock PC: {str(e)}"

    @staticmethod
    def screenshot():
        """Takes a screenshot and saves it."""
        try:
            path = os.path.join(os.path.expanduser("~"), "Pictures", "Veda_Screenshot.png")
            pyautogui.screenshot(path)
            return f"Screenshot saved to Pictures folder"
        except Exception as e:
            return f"Failed to take screenshot: {str(e)}"
