import webbrowser
import urllib.parse

class CommsModule:
    def send_email(self, recipient="", subject="", body=""):
        try:
            url = f"mailto:{recipient}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            webbrowser.open(url)
            return f"COMMS LINK: Dispatching neural draft to {recipient or 'target'}. interface established."
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
                return f"COMMS RELAY: Established connection to {platform} interface."
            return f"COMMS: Platform '{platform}' not found in tactical registry."
        except: return "Relay connection failed."
