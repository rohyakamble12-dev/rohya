import requests
from veda.features.base import VedaPlugin, PermissionTier
from veda.core.governance import governance

class IOTPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("iot_control", self.trigger_webhook, PermissionTier.CONFIRM_REQUIRED,
                            permissions=["iot_access"], risk_level="Moderate",
                            input_schema={"type": "object", "properties": {"device": {"type": "string"}, "action": {"type": "string"}, "url": {"type": "string"}}, "required": ["device", "action", "url"], "additionalProperties": False})

    def validate_params(self, intent, params):
        url = params.get("url", "")
        # SSRF Protection: Restricting IOT triggers to local or whitelisted domains
        if not url.startswith(("http://192.168.", "http://10.", "http://localhost")):
            if not governance.is_domain_authorized(url):
                 return False, "SSRF Block: External IOT endpoint not in tactical whitelist."
        return True, "Valid."

    def trigger_webhook(self, params):
        from veda.utils.network import network
        url = params.get("url")
        data = params.get("data", {})

        # Use safe_post which includes domain and SSRF checks
        res = network.safe_post(url, json_data=data, timeout=5)
        if "Security Violation" in res: return res
        if "Network Error" in res: return f"IOT Transmission Error: {res}"

        return "IOT Protocol sequence complete."
