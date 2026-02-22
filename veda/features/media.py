import pyautogui
import webbrowser
import requests
import re
import urllib.parse
from veda.features.base import VedaPlugin, PermissionTier

class MediaPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
        self.register_intent("play_music", self.play_song, PermissionTier.SAFE)
        self.register_intent("media_control", self.media_control, PermissionTier.SAFE)

    def play_song(self, params):
        song_name = params.get("song_name")
        if not song_name: return "Specify a song."
        try:
            query = urllib.parse.quote(song_name)
            url = f"https://www.youtube.com/results?search_query={query}"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
            if video_ids:
                webbrowser.open(f"https://www.youtube.com/watch?v={video_ids[0]}")
                return f"Acoustic synchronization complete. Playing {song_name}."
            return f"Initiating search for {song_name}."
        except Exception as e:
            return f"Media sync failed: {e}"

    def media_control(self, params):
        cmd = params.get("command", "play_pause")
        keys = {"next": "nexttrack", "prev": "prevtrack", "stop": "stop", "play_pause": "playpause"}
        key = keys.get(cmd, "playpause")
        pyautogui.press(key)
        return f"Media protocol '{cmd}' executed."
