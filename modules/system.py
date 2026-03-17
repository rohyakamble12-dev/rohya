import os
import subprocess
import psutil
import pyautogui
import ctypes

try:
    import pygetwindow as gw
except: gw = None

class SystemModule:
    def open_app(self, app_name):
        try:
            app = app_name.lower().strip()
            aliases = {"chrome": "chrome", "notepad": "notepad", "calculator": "calc"}
            app = aliases.get(app, app)
            subprocess.Popen(f"start {app}", shell=True)
            return f"Executing {app_name}."
        except Exception as e: return f"Execution failed: {e}"

    def close_app(self, app_name):
        if not gw: return "Window management offline."
        try:
            wins = gw.getWindowsWithTitle(app_name)
            if wins:
                wins[0].close()
                return f"Closing {app_name}."
            return "Interface not found."
        except Exception as e: return f"Closure failed: {e}"

    def screenshot(self):
        os.makedirs("captures", exist_ok=True)
        path = f"captures/shot_{int(ctypes.windll.kernel32.GetTickCount64())}.png"
        pyautogui.screenshot(path)
        return f"Tactical capture saved to {path}."

    def get_health(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return f"System Integrity: CPU {cpu}% | RAM {ram}%"

    def lock_pc(self):
        ctypes.windll.user32.LockWorkStation()
        return "OS Locked."
