import os
import subprocess
try:
    if os.environ.get('DISPLAY'):
        import pyautogui
    else:
        pyautogui = None
except (ImportError, KeyError):
    pyautogui = None
import webbrowser
import re
import time
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER, HRESULT
    from comtypes import CLSCTX_ALL
    import pythoncom
except (ImportError, AttributeError):
    # Fallback for non-Windows environments to allow discovery
    AudioUtilities = None
    IAudioEndpointVolume = None
    cast = None
    POINTER = None
    CLSCTX_ALL = None

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None

from veda.features.base import VedaPlugin, PermissionTier
from veda.utils.sandbox import sandbox

class SystemPlugin(VedaPlugin):
    def setup(self):
        # 1. Strict Intent Whitelist with RBAC metadata and Tactical Contracts
        self.register_intent("open_app", self.open_app, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"], "additionalProperties": False})

        self.register_intent("close_app", self.close_app, PermissionTier.CONFIRM_REQUIRED,
                            input_schema={"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"], "additionalProperties": False})

        self.register_intent("set_volume", self.set_volume, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"level": {"type": "integer", "minimum": 0, "maximum": 100}}, "required": ["level"], "additionalProperties": False})

        self.register_intent("set_brightness", self.set_brightness, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"level": {"type": "integer", "minimum": 0, "maximum": 100}}, "required": ["level"], "additionalProperties": False})

        self.register_intent("lock_pc", self.lock_pc, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}})
        self.register_intent("sleep", self.system_sleep, PermissionTier.CONFIRM_REQUIRED,
                            input_schema={"type": "object", "properties": {}})
        self.register_intent("mute_toggle", self.toggle_mute, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}})
        self.register_intent("screenshot", self.screenshot, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}})

        self.register_intent("web_find", self.web_find, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"], "additionalProperties": False})

        self.register_intent("empty_trash", self.empty_recycle_bin, PermissionTier.CONFIRM_REQUIRED,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("set_wallpaper", self.set_wallpaper, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False})

        self.register_intent("shutdown", self.shutdown_pc, PermissionTier.CONFIRM_REQUIRED,
                            input_schema={"type": "object", "properties": {}})
        self.register_intent("restart", self.restart_pc, PermissionTier.CONFIRM_REQUIRED,
                            input_schema={"type": "object", "properties": {}})

        self.register_intent("world_monitor", self.open_world_monitor, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}})

        self.register_intent("shell_isolated", self.shell_isolated, PermissionTier.ADMIN,
                            input_schema={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"], "additionalProperties": False})

    def _get_app_whitelist(self):
        return ["chrome", "notepad", "calculator", "vscode", "zoom", "spotify", "explorer", "cmd", "powershell", "taskmgr", "control", "winword", "excel", "powerpnt"]

    def validate_params(self, intent, params):
        # 2. Strict Parameter Validation
        if 'app_name' in params:
            app = sandbox.filter_app_name(params['app_name'])
            # User Request: If app not found locally, we try web.
            # So we must allow the intent to proceed to open_app even if not in the "known safe" whitelist.
            params['app_name'] = app

        if 'command' in params:
            if not sandbox.validate_shell(params['command']):
                return False, "Security Alert: Malicious shell pattern detected."

        return True, "Valid."

    def predict_impact(self, intent, params):
        if intent == "close_app":
            return f"Impact: Targeted termination of '{params.get('app_name')}' process."
        if intent == "empty_trash":
            return "Impact: Permanent deletion of all items in Recycle Bin."
        return super().predict_impact(intent, params)

    def _sanitize(self, text):
        return re.sub(r'[^a-zA-Z0-9\s._-]', '', str(text)).strip()

    def open_app(self, params):
        app_name = params.get("app_name", "").lower()

        # Tactical Aliases
        aliases = {
            "chrome": "chrome.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe"
        }

        executable = aliases.get(app_name, app_name)
        if not executable.endswith(".exe") and "." not in executable:
             executable += ".exe"

        # os.startfile is safer than os.system
        try:
            if hasattr(os, 'startfile'):
                os.startfile(executable)
                return f"Opening {app_name}."
            else:
                subprocess.Popen([executable], shell=False)
                return f"Opening {app_name}."
        except Exception as e:
            # Fallback for common apps that might not be in PATH
            try:
                subprocess.Popen(executable, shell=False)
                return f"Opening {app_name}."
            except:
                # User Request: If app not found, search web but do NOT open browser.
                web_plugin = self.assistant.plugins.get_plugin("WebPlugin")
                if web_plugin:
                    intel = web_plugin.search({"query": f"detailed summary of the application {app_name}"})
                    if intel and "Zero matches" not in intel:
                         return f"Sir, I couldn't find '{app_name}' locally. Initiating web search sequence. My web intelligence reports:\n\n{intel}"

                return f"Sir, I couldn't find '{app_name}' locally, and tactical web intelligence provides no data on this application."

    def close_app(self, params):
        app_name = params.get("app_name", "")
        # taskkill is safer than raw shell if we control args
        subprocess.run(["taskkill", "/f", "/im", f"{app_name}.exe"], capture_output=True)
        return f"Attempted to terminate {app_name}."

    def set_volume(self, params):
        level = params.get("level", 50)
        try:
            pythoncom.CoInitialize()
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(float(level) / 100, None)
            return f"Volume set to {level}%."
        except Exception as e:
            return f"Volume control failed: {e}"
        finally:
            try: pythoncom.CoUninitialize()
            except: pass

    def set_brightness(self, params):
        if not sbc: return "Brightness control library missing or incompatible."
        try:
            level = params.get("level", 50)
            sbc.set_brightness(int(level))
            return f"Brightness set to {level}%."
        except Exception as e:
            return f"Brightness control failed: {e}"

    def lock_pc(self, params):
        # Using subprocess for better control than os.system
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], capture_output=True)
        return "System locked."

    def system_sleep(self, params):
        # Using subprocess with explicit args
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], capture_output=True)
        return "Suspending system."

    def toggle_mute(self, params):
        try:
            pythoncom.CoInitialize()
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            is_muted = volume.GetMute()
            volume.SetMute(not is_muted, None)
            return "Mute toggled: " + ("OFF" if is_muted else "ON")
        except Exception as e:
            return f"Mute control failed: {e}"
        finally:
            try: pythoncom.CoUninitialize()
            except: pass

    def screenshot(self, params):
        if not pyautogui: return "Screenshot capability restricted (pyautogui missing)."
        save_dir = os.path.join(os.path.expanduser("~"), "Pictures")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"Veda_Screenshot_{int(time.time())}.png")
        pyautogui.screenshot(save_path)
        return f"Screenshot saved to Pictures as Veda_Screenshot_{int(time.time())}.png"

    def web_find(self, params):
        import urllib.parse
        query = params.get('query', '')
        # Sanitize query to prevent argument injection in the browser command
        safe_query = urllib.parse.quote(query)
        webbrowser.open(f"https://www.google.com/search?q={safe_query}")
        return "Searching..."

    def open_world_monitor(self, params):
        """Strategic Visual Intel: Opens World Monitor dashboard."""
        url = "https://worldmonitor.app/"
        try:
            webbrowser.open(url)
            return "Displaying the World Monitor on your primary screen now, Sir."
        except Exception as e:
            return f"I'm unable to initialize the visual monitor: {e}"

    def empty_recycle_bin(self, params):
        try:
            import winshell
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)
            return "Recycle bin purged."
        except ImportError:
            return "Sir, winshell library is missing. I cannot purge the bin manually."
        except Exception as e:
            return f"Recycle bin purge failed: {e}"

    def set_wallpaper(self, params):
        path = sandbox.sanitize_path(params.get("path", ""))
        if not path or not os.path.exists(path): return "Invalid wallpaper path."

        import ctypes
        # SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
        return "Wallpaper updated."

    def shutdown_pc(self, params):
        subprocess.run(["shutdown", "/s", "/t", "30"], capture_output=True)
        return "System shutdown sequence initiated (30s delay)."

    def restart_pc(self, params):
        subprocess.run(["shutdown", "/r", "/t", "30"], capture_output=True)
        return "System restart sequence initiated (30s delay)."

    def shell_isolated(self, params):
        from veda.utils.sandbox import shell
        return shell.execute(params.get("command", "echo Veda Runtime Active"))
