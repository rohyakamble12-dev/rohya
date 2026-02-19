import pyautogui

class VedaMedia:
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
