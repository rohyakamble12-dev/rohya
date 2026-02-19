import pyautogui
import webbrowser
import requests
import re
import urllib.parse

class VedaMedia:
    @staticmethod
    def play_song(song_name):
        """Searches YouTube and plays the first result."""
        try:
            query = urllib.parse.quote(song_name)
            url = f"https://www.youtube.com/results?search_query={query}"
            response = requests.get(url)

            # Simple regex to find the first video ID
            video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
            if video_ids:
                video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                webbrowser.open(video_url)
                return f"Playing {song_name} on YouTube."
            else:
                # Fallback to search results if no direct ID found
                webbrowser.open(url)
                return f"Searching for {song_name} on YouTube."
        except Exception as e:
            return f"Failed to play song: {str(e)}"

    @staticmethod
    def play_pause():
        pyautogui.press('playpause')
        return "Toggled media playback."

    @staticmethod
    def next_track():
        pyautogui.press('nexttrack')
        return "Skipping to the next track."

    @staticmethod
    def prev_track():
        pyautogui.press('prevtrack')
        return "Returning to the previous track."

    @staticmethod
    def stop_media():
        pyautogui.press('stop')
        return "Media playback stopped."
