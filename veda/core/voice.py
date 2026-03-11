import asyncio
import edge_tts
import pyttsx3
import speech_recognition as sr
import pygame
import os
import tempfile
import threading
import json

try:
    from vosk import Model, KaldiRecognizer
    import pyaudio
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

class VedaVoice:
    def __init__(self, online_voice="en-US-AvaNeural"):
        self.online_voice = online_voice
        self.speech_lock = threading.Lock()
        self.recognizer = sr.Recognizer()

        # Resilient Audio Init
        try:
            self.offline_engine = pyttsx3.init()
            pygame.mixer.init()
        except Exception as e:
            print(f"[SYSTEM]: Audio hardware link failed: {e}")
            self.offline_engine = None

        # Load Vosk model if available
        self.vosk_model = None
        if VOSK_AVAILABLE:
            model_path = "veda/storage/vosk-model-small-en-us-0.15"
            if os.path.exists(model_path):
                try:
                    self.vosk_model = Model(model_path)
                except: pass

    async def _speak_online(self, text):
        """Uses Edge TTS to generate and play speech."""
        communicate = edge_tts.Communicate(text, self.online_voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            await communicate.save(tmp_file.name)
            self.play_audio(tmp_file.name)
            os.unlink(tmp_file.name)

    def speak_offline(self, text):
        """Uses pyttsx3 for offline speech."""
        if self.offline_engine:
            try:
                self.offline_engine.say(text)
                self.offline_engine.runAndWait()
            except: pass

    def play_audio(self, file_path):
        """Plays an audio file using pygame."""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
        except: pass

    def speak(self, text):
        """Tiered speech output with hardware fallback."""
        with self.speech_lock:
            try:
                asyncio.run(self._speak_online(text))
            except Exception as e:
                # Silent failure if no audio hardware
                self.speak_offline(text)

    def listen(self):
        """Tiered recognition: Google (Online) -> Vosk (Offline)."""
        try:
            with sr.Microphone() as source:
                print("[LISTENING]...")
                self.recognizer.pause_threshold = 1
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

            print("[RECOGNIZING: ONLINE]...")
            return self.recognizer.recognize_google(audio, language='en-US')
        except Exception:
            if self.vosk_model:
                print("[RECOGNIZING: OFFLINE]...")
                return self._listen_vosk()
            return "None"

    def _listen_vosk(self):
        """Offline speech recognition using Vosk."""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
            stream.start_stream()

            rec = KaldiRecognizer(self.vosk_model, 16000)
            while True:
                data = stream.read(4000, exception_on_overflow=False)
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    return result.get("text", "None")
        except:
            return "None"
        return "None"

    def listen_for_wake_word(self, wake_word="veda"):
        query = self.listen().lower()
        return wake_word in query
