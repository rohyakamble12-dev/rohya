import webbrowser

class SocialPlugin:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "post_social": self.post_to_social
        }

    def post_to_social(self, params):
        platform = params.get("platform", "twitter").lower()
        text = params.get("text", "")

        # Using web-intent URLs as a privacy-respecting and credential-free approach
        if "twitter" in platform or "x" in platform:
            url = f"https://twitter.com/intent/tweet?text={text}"
            webbrowser.open(url)
            return "Redirecting to X/Twitter with your message."
        elif "linkedin" in platform:
            url = f"https://www.linkedin.com/sharing/share-offsite/?url={text}"
            webbrowser.open(url)
            return "Redirecting to LinkedIn share interface."

        return f"Platform {platform} not yet integrated into tactical links."
