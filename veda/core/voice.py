import asyncio
import edge_tts
import pyttsx3
import speech_recognition as sr
import pygame
import os
import tempfile

class VedaVoice:
    def __init__(self, online_voice="en-US-AvaNeural"):
        self.online_voice = online_voice
        self.offline_engine = pyttsx3.init()
        self.setup_offline_voice()
        self.recognizer = sr.Recognizer()
        pygame.mixer.init()

    def setup_offline_voice(self):
        """Sets the offline engine to a female voice if available."""
        voices = self.offline_engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                self.offline_engine.setProperty('voice', voice.id)
                break

    async def speak_online(self, text):
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
        pygame.mixer.music.unload()  # Unload to release the file lock on Windows

    def speak(self, text):
        """Main speak method that tries online TTS first, then falls back to offline."""
        try:
            # edge-tts is async, so we run it in a new event loop or the current one
            asyncio.run(self.speak_online(text))
        except Exception as e:
            print(f"Online TTS failed, falling back to offline: {e}")
            self.speak_offline(text)

    def listen(self):
        """Listens for user input via microphone."""
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.pause_threshold = 1
            audio = self.recognizer.listen(source)

        try:
            print("Recognizing...")
            query = self.recognizer.recognize_google(audio, language='en-US')
            print(f"User said: {query}\n")
            return query
        except Exception as e:
            print("Say that again please...")
            return "None"

    def listen_for_wake_word(self, wake_word="veda"):
        """Simplified wake word detection."""
        query = self.listen().lower()
        if wake_word in query:
            return True
        return False
