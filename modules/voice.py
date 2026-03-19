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
        # Forced high-quality female profile
        self.online_voice = "en-US-AvaNeural"
        self.wake_word = config['preferences']['voice']['wake_word']
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

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
            while pygame.mixer.music.get_busy(): time.sleep(0.1)
            pygame.mixer.music.unload()
            os.unlink(tmp.name)

    def speak(self, text):
        try: asyncio.run(self._speak_online(text))
        except:
            if self.offline_engine:
                self.offline_engine.say(text)
                self.offline_engine.runAndWait()

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

    def listen_passive(self):
        return self.wake_word in self.listen(timeout=2).lower()
