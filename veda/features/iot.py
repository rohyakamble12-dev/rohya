import requests
from veda.features.base import VedaPlugin, PermissionTier

class IOTPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("iot_control", self.trigger_webhook, PermissionTier.CONFIRM_REQUIRED)

    def trigger_webhook(self, params):
        return f"IOT signal sent to {params.get('url')}."
