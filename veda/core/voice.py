import asyncio
import edge_tts
import pyttsx3
import speech_recognition as sr
import pygame
import os
import tempfile
import threading

class VedaVoice:
    def __init__(self, online_voice="en-US-AvaNeural"):
        self.online_voice = online_voice
        self.offline_engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.speech_lock = threading.Lock()
        pygame.mixer.init()

    async def _speak_online(self, text):
        """Uses Edge TTS to generate and play speech."""
        communicate = edge_tts.Communicate(text, self.online_voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            await communicate.save(tmp_file.name)
            self.play_audio(tmp_file.name)
            os.unlink(tmp_file.name)

    def speak_offline(self, text):
        """Uses pyttsx3 for offline speech."""
        self.offline_engine.say(text)
        self.offline_engine.runAndWait()

    def play_audio(self, file_path):
        """Plays an audio file using pygame."""
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()

    def speak(self, text):
        """Tiered speech output with resource locking."""
        with self.speech_lock:
            try:
                asyncio.run(self._speak_online(text))
            except Exception as e:
                print(f"[VOICE]: Online link unstable, switching to offline: {e}")
                self.speak_offline(text)

    def listen(self):
        """Listens for user input via microphone."""
        with sr.Microphone() as source:
            print("[LISTENING]...")
            self.recognizer.pause_threshold = 1
            audio = self.recognizer.listen(source)

        try:
            print("[RECOGNIZING]...")
            query = self.recognizer.recognize_google(audio, language='en-US')
            print(f"[VOICE LINK]: {query}\n")
            return query
        except Exception:
            return "None"
