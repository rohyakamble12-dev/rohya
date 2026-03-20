import webbrowser
import urllib.parse

class CommsModule:
    def send_email(self, recipient="", subject="", body=""):
        try:
            url = f"mailto:{recipient}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            webbrowser.open(url)
            return f"Comms link established. Dispatching neural draft to {recipient or 'target'}."
        except Exception as e:
            return f"Email dispatch failed: {e}"

    def open_social(self, platform):
        urls = {
            "whatsapp": "https://web.whatsapp.com",
            "discord": "https://discord.com/app",
            "telegram": "https://web.telegram.org",
            "slack": "https://slack.com"
        }
        try:
            target = urls.get(platform.lower())
            if target:
                webbrowser.open(target)
                return f"Established connection to {platform} relay."
            return f"Platform '{platform}' not found in tactical comms registry."
        except: return "Relay connection failed."
