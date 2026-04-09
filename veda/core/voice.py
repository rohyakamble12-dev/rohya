import asyncio
import edge_tts
import pyttsx3
import speech_recognition as sr
import pygame
import os
import tempfile
import re
import threading

class VedaVoice:
    def __init__(self, online_voice="en-US-AvaNeural"):
        self.online_voice = online_voice
        self.persona = "friday"
        self.speech_lock = threading.Lock()
        try:
            self.offline_engine = pyttsx3.init()
            self.setup_offline_voice()
        except Exception as e:
            print(f"Offline TTS Unavailable: {e}")
            self.offline_engine = None
        self.recognizer = sr.Recognizer()
        # Pre-initialize microphone to reduce latency
        try:
            self.mic = sr.Microphone()
        except Exception as e:
            print(f"Microphone Unreachable: {e}")
            self.mic = None
        self._is_calibrated = False

        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception as e:
                print(f"Pygame mixer init error: {e}")

    def setup_offline_voice(self):
        """Sets the offline engine voice based on current persona."""
        if not self.offline_engine: return
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
        # On Windows, we need to close the file before Edge TTS can write to it or pygame can read it
        fd, path = tempfile.mkstemp(suffix=".mp3")
        try:
            os.close(fd)
            await communicate.save(path)
            self.play_audio(path)
        finally:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except Exception as e:
                print(f"Sovereign Cleanup Alert: Could not remove voice buffer: {e}")

    def speak_offline(self, text):
        """Uses pyttsx3 for offline speech."""
        if not self.offline_engine:
             print("Sovereign Failure: No offline voice engine available.")
             return
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

        # Thread Safety: Prevent concurrent speech from multiple sources
        with self.speech_lock:
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

    def listen(self, timeout=None):
        """Listens for user input via microphone with optional timeout."""
        if not self.mic:
             return "None"

        try:
            with self.mic as source:
                # Performance: Calibration bypass to eliminate 0.2s delay per cycle
                if not self._is_calibrated:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    self._is_calibrated = True

                self.recognizer.pause_threshold = 0.6
                # Use phrase_time_limit to prevent indefinite blocking
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=8)

            query = self.recognizer.recognize_google(audio, language='en-US')
            return query
        except sr.WaitTimeoutError:
            return "None"
        except Exception:
            return "None"

    def listen_for_wake_word(self, wake_word="veda"):
        """Sovereign wake word detection. Handles blocking and thread-safety."""
        # Non-blocking listen with short timeout for the loop
        query = self.listen(timeout=2)
        if query == "None":
            return None

        ql = query.lower()
        if wake_word in ql:
            return query
        return None
