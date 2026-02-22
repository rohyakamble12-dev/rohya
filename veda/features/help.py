from veda.features.base import VedaPlugin, PermissionTier

class HelpPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("help", self.get_help, PermissionTier.SAFE)

    def get_help(self, params):
        return "I am Veda. Command list available via HUD."
