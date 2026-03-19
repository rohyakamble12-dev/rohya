import os
import subprocess
import psutil
import pyautogui
import ctypes
import logging

try:
    import pygetwindow as gw
except: gw = None

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from ctypes import cast, POINTER
    HAS_PYCAW = True
except: HAS_PYCAW = False

try:
    import screen_brightness_control as sbc
    HAS_SBC = True
except: HAS_SBC = False

class SystemModule:
    def open_app(self, app_name):
        try:
            if not app_name: return "App name required."
            app = app_name.lower().strip()
            # Strict normalization to prevent command injection
            import re
            safe_app = re.sub(r'[^a-zA-Z0-9\s.:/-]', '', app)

            aliases = {"chrome": "chrome", "notepad": "notepad", "calculator": "calc", "explorer": "explorer"}
            cmd = aliases.get(safe_app, safe_app)

            # Using start command safely on Windows
            subprocess.Popen(f"start {cmd}", shell=True)
            return f"Executing {app_name}."
        except Exception as e: return f"Execution failed: {e}"

    def move_file(self, src, dst):
        try:
            import shutil
            if os.path.exists(src):
                shutil.move(src, dst)
                return f"Relocated {os.path.basename(src)} to target destination."
            return "Source archive not found."
        except Exception as e: return f"Relocation failed: {e}"

    def close_app(self, app_name):
        if not gw: return "Window management offline."
        try:
            wins = gw.getWindowsWithTitle(app_name)
            if wins:
                for win in wins:
                    win.close()
                return f"Closing {app_name}."
            return f"No active interface for {app_name} found."
        except Exception as e: return f"Closure failed: {e}"

    def set_volume(self, level):
        if not HAS_PYCAW: return "Audio interface link broken."
        try:
            level = max(0, min(100, int(level)))
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return f"Audio output optimized to {level}%."
        except Exception as e: return f"Audio adjustment failed: {e}"

    def set_brightness(self, level):
        if not HAS_SBC: return "Optic brightness link broken."
        try:
            level = max(0, min(100, int(level)))
            sbc.set_brightness(level)
            return f"Display brightness synchronized to {level}%."
        except Exception as e: return f"Brightness adjustment failed: {e}"

    def screenshot(self):
        try:
            os.makedirs("captures", exist_ok=True)
            path = f"captures/shot_{int(ctypes.windll.kernel32.GetTickCount64())}.png"
            pyautogui.screenshot(path)
            return f"Tactical capture saved to {path}."
        except Exception as e: return f"Capture failed: {e}"

    def get_health(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            return f"INTEGRITY: CPU {cpu}% | RAM {ram}% | DSK {disk}%"
        except Exception as e: return f"Diagnostic failure: {e}"

    def lock_pc(self):
        try:
            ctypes.windll.user32.LockWorkStation()
            return "OS Locked. Tactical security engaged."
        except Exception as e: return f"Lock failed: {e}"
