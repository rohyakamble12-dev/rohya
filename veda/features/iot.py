import requests

class VedaIOT:
    @staticmethod
    def trigger_webhook(url, method="POST", data=None):
        """Generic handler to trigger smart home webhooks (IFTTT, Home Assistant, etc.)"""
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=data, timeout=5)
            else:
                response = requests.get(url, timeout=5)

            if response.status_code in [200, 201]:
                return "Signal transmitted successfully. Smart device responding."
            return f"Transmission error: Device returned status {response.status_code}."
        except Exception as e:
            return f"IOT Protocol failure: {str(e)}"

    @staticmethod
    def light_control(state):
        """Specific command for a hypothetical light controller."""
        # This is a placeholder for actual IOT integration
        return f"Protocol engaged. Switching lights to {state.upper()}."
