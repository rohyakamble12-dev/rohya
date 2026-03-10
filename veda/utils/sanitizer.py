import re

class VedaSanitizer:
    @staticmethod
    def clean_input(text):
        """Removes wake words, punctuation, and extra whitespace."""
        if not text:
            return ""

        # Lowercase and strip first
        cleaned = text.lower().strip()

        # Remove common prefixes followed by optional punctuation like comma
        prefixes = [r"^veda[,\s]*", r"^hey veda[,\s]*", r"^please[,\s]*", r"^friday[,\s]*", r"^hey friday[,\s]*"]

        for p in prefixes:
            cleaned = re.sub(p, "", cleaned).strip()

        # Remove trailing punctuation
        cleaned = re.sub(r"[?!.,]$", "", cleaned)

        return cleaned.strip()

    @staticmethod
    def normalize_app_name(app_name):
        """Sanitizes application names for system calls."""
        return re.sub(r"[^a-zA-Z0-9\s:-]", "", app_name).strip()
