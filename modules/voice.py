import asyncio, edge_tts, pyttsx3, os, tempfile, pygame, time, json
import speech_recognition as sr

try:
    from vosk import Model, KaldiRecognizer
    import pyaudio
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

class VedaVoice:
    def __init__(self, config):
        self.config = config
        self.active_id = config.get("identity", {}).get("active_id", "FRIDAY")
        self._update_voice_profile()
        self.wake_word = config['preferences']['voice']['wake_word']
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.mic_level = 0.0

        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            self.offline_engine = pyttsx3.init()
            # Enforce female offline identity
            voices = self.offline_engine.getProperty('voices')
            for voice in voices:
                if "female" in voice.name.lower() or "zira" in voice.name.lower():
                    self.offline_engine.setProperty('voice', voice.id)
                    break
            pygame.mixer.init()
        except: self.offline_engine = None

    async def _speak_online(self, text):
        communicate = edge_tts.Communicate(text, self.online_voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            await communicate.save(tmp.name)
            pygame.mixer.music.load(tmp.name)
            pygame.mixer.music.play()

            # Simulated Speech Visualization Link
            while pygame.mixer.music.get_busy():
                # Fluctuating mic_level for HUD animation
                self.mic_level = 0.5 + (0.5 * (time.time() % 0.5))
                time.sleep(0.05)

            self.mic_level = 0.0
            pygame.mixer.music.unload()
            os.unlink(tmp.name)

    def speak(self, text):
        """Unified speech output with priority for high-quality online TTS."""
        try:
            # Check if event loop is already running (e.g. within an async context)
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                # If loop is already running (which shouldn't happen here but for safety)
                # we can't use run_until_complete easily without nesting.
                # But typically main.py calls this from a thread.
                future = asyncio.run_coroutine_threadsafe(self._speak_online(text), loop)
                future.result()
            else:
                loop.run_until_complete(self._speak_online(text))
        except Exception:
            # Fallback to offline pyttsx3 (SAPI5 on Windows)
            if self.offline_engine:
                try:
                    self.offline_engine.say(text)
                    self.offline_engine.runAndWait()
                except: pass

    def listen(self, timeout=5):
        try:
            # Tier 1: Online
            with self.mic as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            return self.recognizer.recognize_google(audio)
        except:
            # Tier 2: Offline
            if VOSK_AVAILABLE: return self._listen_vosk()
            return ""

    def _listen_vosk(self):
        try:
            model_path = "storage/vosk-model-small-en-us-0.15"
            if not os.path.exists(model_path): return ""
            model = Model(model_path)
            rec = KaldiRecognizer(model, 16000)
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
            stream.start_stream()
            start_time = time.time()
            while time.time() - start_time < 8:
                data = stream.read(4000, exception_on_overflow=False)
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    return res.get("text", "")
            return ""
        except: return ""

    def _update_voice_profile(self):
        """Switches vocal profile based on active identity."""
        if self.active_id == "JARVIS":
            self.online_voice = "en-GB-RyanNeural" # Sophisticated British male
        else:
            self.online_voice = "en-US-AvaNeural" # Professional female

        if hasattr(self, 'offline_engine') and self.offline_engine:
            voices = self.offline_engine.getProperty('voices')
            for voice in voices:
                if self.active_id == "JARVIS":
                    if "david" in voice.name.lower() or "male" in voice.name.lower():
                        self.offline_engine.setProperty('voice', voice.id)
                        break
                else:
                    if "zira" in voice.name.lower() or "female" in voice.name.lower():
                        self.offline_engine.setProperty('voice', voice.id)
                        break

    def switch_identity(self, identity):
        self.active_id = identity.upper()
        self._update_voice_profile()
        return f"Identity relay synchronized to {self.active_id} protocol."

    def listen_passive(self):
        return self.wake_word in self.listen(timeout=2).lower()
