import re

class VedaPrivacy:
    @staticmethod
    def _get_blacklist():
        try:
            from veda.core.governance import governance
            return governance.privacy_blacklist
        except Exception:
            return ["banking", "password", "crypto-wallet", "login", "auth", "secret"]

    @staticmethod
    def scrub(text):
        """Zero-Trust: Redacts sensitive keywords from text."""
        if not text: return ""
        scrubbed = str(text)
        for word in VedaPrivacy._get_blacklist():
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            scrubbed = pattern.sub("[REDACTED]", scrubbed)
        return scrubbed

# Single Utility
privacy = VedaPrivacy()
