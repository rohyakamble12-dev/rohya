import os
try:
    if os.environ.get('DISPLAY'):
        import pyautogui
    else:
        pyautogui = None
except (ImportError, KeyError):
    pyautogui = None
import webbrowser
import requests
import re
import urllib.parse
from veda.features.base import VedaPlugin, PermissionTier

class MediaPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("play_music", self.play_song, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"song_name": {"type": "string"}}, "required": ["song_name"], "additionalProperties": False})
        self.register_intent("media_control", self.media_control, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"command": {"enum": ["next", "prev", "stop", "play_pause"]}}, "required": ["command"], "additionalProperties": False})

    def play_song(self, params):
        song = params.get("song_name")
        webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(song)}")
        return f"Acoustic sequence for '{song}' initiated."

    def media_control(self, params):
        if not pyautogui: return "Media keys restricted (pyautogui missing)."
        cmd = params.get("command", "play_pause")
        keys = {"next": "nexttrack", "prev": "prevtrack", "stop": "stop", "play_pause": "playpause"}
        try:
            pyautogui.press(keys.get(cmd, "playpause"))
            return f"Vocal command '{cmd}' executed."
        except Exception as e:
            return f"Tactical Media Failure: {e}"
