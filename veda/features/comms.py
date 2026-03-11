import webbrowser
import urllib.parse

class CommsPlugin:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "send_email": self.compose_email
        }

    def compose_email(self, params):
        to = params.get("to", "")
        subject = params.get("subject", "Message from Veda")
        body = params.get("body", "")

        # We use mailto: as it is local-first and privacy-respecting (doesn't require SMTP credentials)
        # and leverages the user's default OS email client.
        subject_enc = urllib.parse.quote(subject)
        body_enc = urllib.parse.quote(body)
        mailto_url = f"mailto:{to}?subject={subject_enc}&body={body_enc}"

        try:
            webbrowser.open(mailto_url)
            return f"Opening your email client to message {to}."
        except Exception as e:
            return f"Failed to open email client: {str(e)}"
