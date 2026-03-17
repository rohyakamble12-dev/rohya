import requests

class IOTModule:
    def __init__(self, config):
        self.webhooks = config.get("webhooks", {})

    def trigger(self, device):
        url = self.webhooks.get(device)
        if not url: return f"Device {device} not configured."
        try:
            res = requests.post(url, timeout=5)
            return f"Triggered {device}." if res.status_code == 200 else f"Trigger failed."
        except Exception as e: return f"Link failed: {e}"
