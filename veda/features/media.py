import webbrowser
import os

class MediaPlugin:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "play_youtube": self.youtube_search,
            "media_control": self.control_media
        }

    def youtube_search(self, params):
        query = params.get("query", "")
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching YouTube for {query}."

    def control_media(self, params):
        action = params.get("action", "pause").lower()
        # Uses pyautogui to send media keys
        key_map = {
            "play": "playpause",
            "pause": "playpause",
            "next": "nexttrack",
            "previous": "prevtrack"
        }
        try:
            import pyautogui
            pyautogui.press(key_map.get(action, "playpause"))
            return f"Media {action} command sent."
        except:
            return "Media control failed."
