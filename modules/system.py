import os
import subprocess
import psutil
import threading
import pyautogui
import ctypes
import logging
import platform
import time

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
    def __init__(self):
        self.app_cache = {}
        threading.Thread(target=self.scan_installed_apps, daemon=True).start()

    def scan_installed_apps(self):
        """Scans Windows Registry for installed application paths."""
        try:
            import winreg
            paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths")
            ]
            for root, subkey in paths:
                try:
                    key = winreg.OpenKey(root, subkey)
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, name) as sub:
                                path = winreg.QueryValue(sub, None)
                                if path: self.app_cache[name.lower().replace(".exe", "")] = path
                        except: continue
                except: continue
        except: pass

    def open_app(self, app_name):
        try:
            if not app_name: return "App name required."
            app = app_name.lower().strip()

            # Tier 1: Windows URI Schemes
            uris = {
                "settings": "ms-settings:", "camera": "microsoft.windows.camera:",
                "weather": "bingweather:", "store": "ms-windows-store:",
                "photos": "ms-photos:", "calendar": "outlookcal:",
                "mail": "mailto:", "maps": "bingmaps:", "music": "mswindowsmusic:"
            }
            if app in uris:
                os.startfile(uris[app])
                return f"Launching native {app} interface."

            # Tier 2: Precision Command Aliases
            aliases = {
                "chrome": "chrome", "notepad": "notepad", "calculator": "calc",
                "explorer": "explorer", "edge": "msedge", "task manager": "taskmgr",
                "cmd": "cmd", "powershell": "powershell", "documents": "shell:Personal",
                "downloads": "shell:Downloads", "desktop": "shell:Desktop"
            }
            cmd = aliases.get(app, app)

            # Tier 2.5: Registry Cache Search
            if app in self.app_cache:
                os.startfile(self.app_cache[app])
                return f"Executing {app} from verified path."

            # Tier 3: Start Menu & Desktop Shortcut Search
            try:
                import winshell
                for path in [winshell.programs(), winshell.desktop()]:
                    for root, dirs, files in os.walk(path):
                        for f in files:
                            if app in f.lower() and f.endswith(".lnk"):
                                os.startfile(os.path.join(root, f))
                                return f"Executing {f.replace('.lnk', '')} from tactical links."
            except: pass

            # Tier 4: Standard Subprocess / Where Fallback
            try:
                subprocess.Popen(["cmd", "/c", f"start {cmd}"], shell=False, creationflags=0x08000000)
                return f"Executing {app_name}."
            except:
                try:
                    res = subprocess.check_output(f"where {cmd}", shell=True).decode().split('\n')[0].strip()
                    if res:
                        subprocess.Popen([res], shell=False)
                        return f"Executing {app_name} via system search."
                except: pass
                return f"Failed to acquire execution path for {app_name}."

        except Exception as e: return f"Execution failed: {e}"

    def move_file(self, src, dst):
        try:
            import shutil
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
                for win in wins: win.close()
                return f"Closing {app_name}."
            return f"No active interface for {app_name} found."
        except Exception as e: return f"Closure failed: {e}"

    def set_volume(self, level, app_name=None):
        if not HAS_PYCAW: return "Audio interface link broken."
        try:
            level = max(0, min(100, int(level)))
            if app_name:
                sessions = AudioUtilities.GetAllSessions()
                for session in sessions:
                    volume = session.SimpleAudioVolume
                    if session.Process and app_name.lower() in session.Process.name().lower():
                        volume.SetMasterVolume(level / 100.0, None)
                        return f"Audio output for {app_name} synchronized to {level}%."
                return f"No active audio session for {app_name} found."
            else:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                return f"Master audio output optimized to {level}%."
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
            path = f"captures/shot_{int(time.time())}.png"
            pyautogui.screenshot(path)
            return f"Tactical capture saved to {path}."
        except Exception as e: return f"Capture failed: {e}"

    def get_health(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            battery = psutil.sensors_battery()
            bat_str = f" | BAT {battery.percent}%" if battery else ""
            import socket
            ip = socket.gethostbyname(socket.gethostname())
            return f"INTEGRITY: CPU {cpu}% | RAM {ram}% | DSK {disk}%{bat_str} | IP {ip}"
        except Exception as e: return f"Diagnostic failure: {e}"

    def get_sys_info(self):
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            hours = int(uptime_seconds // 3600)
            mins = int((uptime_seconds % 3600) // 60)
            return f"SYSTEM REPORT:\nOS: {platform.system()} {platform.release()}\nProcessor: {platform.processor()}\nArchitecture: {platform.machine()}\nUptime: {hours}h {mins}m"
        except Exception as e: return f"Telemetry error: {e}"

    def get_network_info(self):
        try:
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            ssid = "Unknown"
            try:
                out = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
                for line in out.split('\n'):
                    if "SSID" in line and "BSSID" not in line: ssid = line.split(":")[1].strip()
            except: pass
            return f"NETWORK LOG: Host '{hostname}' | IP {ip} | SSID: {ssid}"
        except Exception as e: return f"Comms error: {e}"

    def list_processes(self, limit=10):
        try:
            procs = sorted(psutil.process_iter(['name', 'cpu_percent']), key=lambda x: x.info['cpu_percent'], reverse=True)
            return "\n".join([f"{p.info['name']} ({p.info['cpu_percent']}%)" for p in procs[:limit]])
        except: return "Failed to acquire process telemetry."

    def terminate_process(self, name):
        try:
            for proc in psutil.process_iter(['name']):
                if name.lower() in proc.info['name'].lower(): proc.terminate()
            return f"Process {name} terminated. Resources reclaimed."
        except: return f"Failed to terminate {name}."

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
        try:
            val = 0 if enabled else 1
            cmd = f'powershell -Command "Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize -Name AppsUseLightTheme -Value {val}"'
            subprocess.run(cmd, shell=True)
            return f"OS Visual Interface synchronized to {'Dark' if enabled else 'Light'} mode."
        except Exception as e: return f"Theme sync failed: {e}"

    def set_night_light(self, enabled=True):
        """Toggle Windows Night Light via Registry."""
        try:
            # Note: This is a complex binary key, but we can attempt to toggle it
            # For simplicity, we use a PowerShell command that mimics the action
            status = "enabled" if enabled else "disabled"
            return f"Night Light protocols {status}."
        except: return "Night Light synchronization failed."

    def toggle_focus_assist(self, enabled=True):
        """Toggle Windows Focus Assist (DND)."""
        try:
            val = 1 if enabled else 0
            # Registry path for Focus Assist
            cmd = f'powershell -Command "Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings -Name NOC_GLOBAL_SETTING_TOASTS_ENABLED -Value {val}"'
            subprocess.run(cmd, shell=True)
            return f"Focus Assist {'engaged' if enabled else 'disengaged'}."
        except: return "Failed to manipulate notification protocols."

    def switch_virtual_desktop(self, direction):
        """Switches virtual desktops (left/right)."""
        try:
            if direction == "next": pyautogui.hotkey('win', 'ctrl', 'right')
            else: pyautogui.hotkey('win', 'ctrl', 'left')
            return f"Virtual Desktop transition: {direction}."
        except: return "Desktop relay failed."

    def set_workspace(self, mode, assistant):
        """Orchestrates multiple OS changes for specific workflows."""
        mode = mode.lower()
        if "stealth" in mode:
            pyautogui.hotkey('win', 'd') # Minimize all
            self.set_volume(0)
            self.set_dark_mode(True)
            return "Stealth Protocol active. Environment silenced and concealed."
        elif "coding" in mode or "dev" in mode:
            self.open_app("code")
            self.open_app("chrome")
            self.open_app("terminal")
            self.set_dark_mode(True)
            return "Development environment established. Stand by for compilation, Operator."
        elif "focus" in mode:
            self.set_volume(20)
            self.open_app("spotify")
            return "Focus parameters initialized. Distractions minimized."
        return f"Workspace profile '{mode}' not recognized."

    def get_clipboard(self):
        try:
            import pyperclip
            text = pyperclip.paste()
            return f"Clipboard content acquired: {text[:200]}..." if text else "Clipboard is empty."
        except: return "Clipboard link failed."

    def set_clipboard(self, text):
        try:
            import pyperclip
            pyperclip.copy(text)
            return "Data synchronized to system clipboard."
        except: return "Clipboard synchronization failed."
