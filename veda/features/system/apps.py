from veda.features.base import VedaPlugin, PermissionTier
from veda.utils.sandbox import sandbox
import os
import subprocess

class AppControlPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("open_app", self.open_app, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"]})
        self.register_intent("close_app", self.close_app, PermissionTier.CONFIRM_REQUIRED,
                            input_schema={"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"]})

    def open_app(self, params):
        app_name = params.get("app_name", "").lower()
        aliases = {"chrome": "chrome.exe", "word": "winword.exe", "excel": "excel.exe", "powerpoint": "powerpnt.exe"}
        executable = aliases.get(app_name, app_name)
        if not executable.endswith(".exe") and "." not in executable: executable += ".exe"
        try:
            if os.name == 'nt': os.startfile(executable)
            else: subprocess.Popen([executable])
            return f"Opening {app_name}."
        except:
            web_plugin = self.assistant.plugins.get_plugin("WebSearchPlugin")
            if web_plugin:
                intel = web_plugin.search({"query": f"detailed summary of the application {app_name}"})
                return f"Sir, I couldn't find '{app_name}' locally. My web intelligence reports:\n\n{intel}"
            return f"Sir, I couldn't find '{app_name}' locally."

    def close_app(self, params):
        app_name = params.get("app_name", "")
        subprocess.run(["taskkill", "/f", "/im", f"{app_name}.exe"], capture_output=True)
        return f"Attempted to terminate {app_name}."
