from veda.features.base import VedaPlugin, PermissionTier

class CommsPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("send_email", self.send_email, PermissionTier.CONFIRM_REQUIRED,
                            input_schema={"type": "object", "properties": {"recipient": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["recipient", "body"], "additionalProperties": False})

    def send_email(self, params):
        """Unified Email Dispatch via OS Integration."""
        import urllib.parse
        import webbrowser

        recipient = params.get('recipient')
        subject = urllib.parse.quote(params.get('subject', 'Veda Tactical Report'))
        body = urllib.parse.quote(params.get('body', ''))

        # Using mailto for a cred-less real-life implementation that opens the default client
        try:
            webbrowser.open(f"mailto:{recipient}?subject={subject}&body={body}")
            return f"Strategic mail client initiated for transmission to {recipient}."
        except Exception:
            return "Comms Node Failure: Could not initiate mail client."
