from veda.features.base import VedaPlugin, PermissionTier
import webbrowser

class WorldMonitorPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("world_monitor", self.open_world_monitor, PermissionTier.SAFE)

    def open_world_monitor(self, params):
        """Strategic Visual Intel: Opens World Monitor dashboard."""
        url = "https://worldmonitor.app/"
        try:
            webbrowser.open(url)
            return "Displaying the World Monitor on your primary screen now, Sir."
        except Exception as e:
            return f"I'm unable to initialize the visual monitor: {e}"
