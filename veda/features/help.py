from veda.features.base import VedaPlugin, PermissionTier

class HelpPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
        self.register_intent("help", self.get_help, PermissionTier.SAFE)

    def get_help(self, params):
        return "I can manage your system, research topics, and automate tasks. Ask for specific help like 'How do I use file search?'."
