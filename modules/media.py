import webbrowser
from deep_translator import GoogleTranslator
import logging

try:
    from pynput.keyboard import Controller, Key
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

class MediaModule:
    def __init__(self):
        self.keyboard = Controller() if KEYBOARD_AVAILABLE else None

    def play_youtube(self, song):
        try:
            # Enhanced to attempt direct playing if possible
            url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}&sp=EgIQAQ%253D%253D" # Filter for videos
            webbrowser.open(url)
            return f"MEDIA PROTOCOL: Searching for '{song}' in global archives. Link established."
        except Exception as e:
            return f"Media link failed: {e}"

    def control(self, action):
        if not self.keyboard: return "Keyboard control offline."
        actions = {"pause": Key.media_play_pause, "play": Key.media_play_pause, "next": Key.media_next, "previous": Key.media_previous}
        key = actions.get(action.lower())
        if key:
            self.keyboard.press(key)
            self.keyboard.release(key)
            return f"Media {action} executed."
        return "Invalid media command."

    def translate(self, text, target_lang="en"):
        try:
            translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
            return f"Translation ({target_lang}): {translated}"
        except Exception as e:
            return f"Translation failed: {e}"
