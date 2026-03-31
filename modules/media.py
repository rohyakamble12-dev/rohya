import webbrowser
import threading
import os
try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False
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

    def download_media(self, query):
        """MCU Accurate Media Archival: Real YouTube audio extraction."""
        try:
            import yt_dlp
            def _download():
                os.makedirs("assets/sounds", exist_ok=True)
                opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
                    'outtmpl': 'assets/sounds/%(title)s.%(ext)s',
                    'quiet': True
                }
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([f"ytsearch1:{query}"])

            threading.Thread(target=_download, daemon=True).start()
            return f"MEDIA ARCHIVAL: '{query}' identified. Background retrieval protocol initiated. Tactical files will be stored in the sounds sector."
        except ImportError:
            return "MEDIA ARCHIVAL: yt-dlp link failed. Manual archival required."
        except Exception as e:
            return f"Media archival protocol failed: {e}"

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
        if not HAS_TRANSLATOR: return "Translation services offline."
        try:
            translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
            return f"Translation ({target_lang}): {translated}"
        except Exception as e:
            return f"Translation failed: {e}"
