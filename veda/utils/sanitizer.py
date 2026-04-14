import re
import html
from veda.utils.logger import logger

class VedaSanitizer:
    @staticmethod
    def sanitize_user_input(text):
        """Zero-Trust Sanitization: Neutralizes potential injection vectors in user input."""
        if not text: return ""

        # 1. Strip HTML tags
        clean_text = re.sub(r'<.*?>', '', text)

        # 2. Escape HTML entities
        clean_text = html.escape(clean_text)

        # 3. Block command injection tokens
        blocked_tokens = [";", "&&", "||", "`", "$(", "system("]
        for token in blocked_tokens:
            if token in clean_text:
                logger.warning(f"Sanitizer: Neutralized dangerous token '{token}' in user input.")
                clean_text = clean_text.replace(token, "[BLOCKED]")

        # 4. Limit length to prevent buffer/token overflow attacks
        return clean_text[:2000].strip()

# Global Sanitizer
sanitizer = VedaSanitizer()
