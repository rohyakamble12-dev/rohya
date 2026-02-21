import asyncio
import edge_tts
import pyttsx3
import speech_recognition as sr
import pygame
import os
import tempfile
import re

class VedaVoice:
    def __init__(self, online_voice="en-US-AvaNeural"):
        self.online_voice = online_voice
        self.persona = "friday"
        self.offline_engine = pyttsx3.init()
        self.setup_offline_voice()
        self.recognizer = sr.Recognizer()
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception as e:
                print(f"Pygame mixer init error: {e}")

    def setup_offline_voice(self):
        """Sets the offline engine voice based on current persona."""
        voices = self.offline_engine.getProperty('voices')
        target = "female" if self.persona == "friday" else "male"
        for voice in voices:
            if target in voice.name.lower() or (target == "female" and "zira" in voice.name.lower()):
                self.offline_engine.setProperty('voice', voice.id)
                break

    def set_persona(self, persona_name):
        """Switches the vocal persona."""
        persona_name = persona_name.lower()
        if persona_name == "jarvis":
            self.online_voice = "en-GB-RyanNeural"
            self.persona = "jarvis"
        else:
            self.online_voice = "en-US-AvaNeural"
            self.persona = "friday"
        self.setup_offline_voice()

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

    def sanitize_text_for_speech(self, text):
        """Removes markdown and special characters that shouldn't be spoken."""
        if not text: return ""
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        # Remove inline code
        text = re.sub(r'`.*?`', '', text)
        # Remove markdown bold/italic asterisks and underscores
        text = re.sub(r'[*_]{1,3}', '', text)
        # Remove hashtags
        text = re.sub(r'#+', '', text)
        # Remove link syntax [text](url) -> text
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        # Remove emojis and other non-standard characters
        text = text.encode('ascii', 'ignore').decode('ascii')
        # Remove symbols that shouldn't be read (except standard punctuation)
        text = re.sub(r'[^\w\s.,?!:;\'"-]', ' ', text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def speak(self, text):
        """Main speak method that tries online TTS first, then falls back to offline."""
        if not text: return

        text = self.sanitize_text_for_speech(text)
        if not text: return

        try:
            # Try online first
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.speak_online(text))
            loop.close()
        except Exception as e:
            print(f"Online TTS failed ({e}), falling back to offline.")
            try:
                self.speak_offline(text)
            except Exception as e2:
                print(f"Offline TTS also failed: {e2}")

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
