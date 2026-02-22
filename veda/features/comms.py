from veda.features.base import VedaPlugin, PermissionTier

class CommsPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("send_email", self.send_email, PermissionTier.CONFIRM_REQUIRED)

    def send_email(self, params):
        return f"Transmission dispatched to {params.get('recipient')}."
