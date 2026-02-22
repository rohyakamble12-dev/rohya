import requests
from veda.features.base import VedaPlugin, PermissionTier

class IOTPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
        self.register_intent("iot_control", self.trigger_webhook, PermissionTier.CONFIRM_REQUIRED)

    def trigger_webhook(self, params):
        url = params.get("url")
        data = params.get("data", {})
        try:
            res = requests.post(url, json=data, timeout=5)
            return f"IOT Signal sent. Status: {res.status_code}."
        except Exception as e:
            return f"IOT Protocol failure: {e}"
