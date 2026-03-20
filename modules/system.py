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

            # Common aliases for Windows
            aliases = {
                "chrome": "chrome",
                "notepad": "notepad",
                "calculator": "calc",
                "explorer": "explorer",
                "edge": "msedge",
                "task manager": "taskmgr",
                "cmd": "cmd",
                "powershell": "powershell",
                "documents": "explorer shell:Personal",
                "downloads": "explorer shell:Downloads",
                "settings": "start ms-settings:",
                "camera": "start microsoft.windows.camera:",
                "weather": "start bingweather:",
                "photos": "start mspaint", # or "start ms-photos:"
                "store": "start ms-windows-store:"
            }

            cmd = aliases.get(app, app)

            # Sanitization (allow letters, numbers, spaces, and certain safe chars)
            import re
            if not re.match(r'^[a-zA-Z0-9\s.:/\\_-]+$', cmd):
                return "Security violation: Invalid command characters detected."

            # Try launching with 'start'
            try:
                # Use list-based Popen to avoid shell injection
                subprocess.Popen(["cmd", "/c", f"start {cmd}"],
                               shell=False,
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                return f"Executing {app_name}."
            except Exception:
                # Advance Search Fallback
                try:
                    # Using where command to find path
                    res = subprocess.check_output(f"where {cmd}", shell=True).decode().split('\n')[0].strip()
                    if res:
                        subprocess.Popen([res], shell=False)
                        return f"Executing {app_name} via system search."
                except: pass

                # Try direct execution
                try:
                    subprocess.Popen([cmd], shell=False)
                    return f"Executing {app_name} via direct link."
                except: return f"Failed to acquire execution path for {app_name}."

        except Exception as e: return f"Execution failed: {e}"

    def move_file(self, src, dst):
        try:
            import shutil

            # Resolve common folder aliases
            user_home = os.path.expanduser("~")
            aliases = {
                "documents": os.path.join(user_home, "Documents"),
                "desktop": os.path.join(user_home, "Desktop"),
                "downloads": os.path.join(user_home, "Downloads"),
                "music": os.path.join(user_home, "Music"),
                "pictures": os.path.join(user_home, "Pictures")
            }

            resolved_src = aliases.get(src.lower(), src)
            resolved_dst = aliases.get(dst.lower(), dst)

            if os.path.exists(resolved_src):
                # Ensure destination directory exists
                if not os.path.exists(resolved_dst) and "." not in os.path.basename(resolved_dst):
                    os.makedirs(resolved_dst, exist_ok=True)

                shutil.move(resolved_src, resolved_dst)
                return f"Relocated {os.path.basename(resolved_src)} to {os.path.basename(resolved_dst) or resolved_dst}."
            return f"Source archive '{src}' not found in active sectors."
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

    def get_active_window(self):
        if not gw: return "Window management offline."
        try:
            win = gw.getActiveWindow()
            return f"Current focus: {win.title}" if win else "No active interface detected."
        except: return "Failed to acquire active focus."

    def manipulate_window(self, action, title=None):
        if not gw: return "Window management offline."
        try:
            target = gw.getActiveWindow() if not title else gw.getWindowsWithTitle(title)[0]
            if not target: return "Target window not found."

            if action == "maximize": target.maximize()
            elif action == "minimize": target.minimize()
            elif action == "restore": target.restore()
            elif action == "close": target.close()
            return f"Window {action} protocol executed."
        except Exception as e: return f"Window manipulation failed: {e}"

    def set_dark_mode(self, enabled=True):
        """Toggle Windows Dark/Light mode via Registry."""
        try:
            val = 0 if enabled else 1
            cmd = f'powershell -Command "Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize -Name AppsUseLightTheme -Value {val}"'
            subprocess.run(cmd, shell=True)
            return f"OS Visual Interface synchronized to {'Dark' if enabled else 'Light'} mode."
        except Exception as e: return f"Theme sync failed: {e}"
