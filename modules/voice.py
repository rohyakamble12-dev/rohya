import asyncio, edge_tts, pyttsx3, os, tempfile, pygame, time
import speech_recognition as sr

class VedaVoice:
    def __init__(self, config):
        self.online_voice = config['preferences']['voice']['online_voice']
        self.wake_word = config['preferences']['voice']['wake_word']
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

        # Pre-calibrate ambient noise
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            self.offline_engine = pyttsx3.init()
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
            with self.mic as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            return self.recognizer.recognize_google(audio)
        except: return ""

    def listen_passive(self):
        """Optimized passive listener with minimal overhead."""
        return self.wake_word in self.listen(timeout=2).lower()
