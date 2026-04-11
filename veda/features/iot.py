import os
import requests

class IOTController:
    @staticmethod
    def trigger_webhook(action=None):
        """Triggers a pre-configured IOT webhook."""
        try:
            # We can use an environment variable or default to a mock
            webhook_url = os.environ.get("IOT_WEBHOOK_URL")

            if not webhook_url:
                return "No IOT Webhook URL configured. Please set the IOT_WEBHOOK_URL environment variable."

            # If there's an action, we can append it as a query param or payload (depends on the service)
            # For simplicity, we'll do a basic GET request
            url = webhook_url
            if action:
                # Basic appending, assume it's IFTTT style
                pass

            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                return "Successfully triggered the IOT protocol."
            else:
                return f"Failed to trigger IOT protocol. Status code: {response.status_code}"

        except Exception as e:
            return f"Error communicating with IOT service: {str(e)}"
