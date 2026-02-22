import pyautogui
import webbrowser
import requests
import re
import urllib.parse
from veda.features.base import VedaPlugin, PermissionTier

class MediaPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("play_music", self.play_song, PermissionTier.SAFE)
        self.register_intent("media_control", self.media_control, PermissionTier.SAFE)

    def play_song(self, params):
        song = params.get("song_name")
        webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(song)}")
        return f"Acoustic sequence for '{song}' initiated."

    def media_control(self, params):
        cmd = params.get("command", "play_pause")
        keys = {"next": "nexttrack", "prev": "prevtrack", "stop": "stop", "play_pause": "playpause"}
        pyautogui.press(keys.get(cmd, "playpause"))
        return f"Vocal command '{cmd}' executed."
