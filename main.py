import requests
import sys
import os
import json
import logging
import threading
import time
from modules.ui import VedaHUD
from modules.voice import VedaVoice
from modules.brain import VedaBrain
from modules.commands import CommandRouter
from modules.memory import VedaMemory
from modules.notifications import NotificationModule

class VedaAssistant:
    def __init__(self):
        self.load_config()
        self.setup_logging()

        # Core Subsystems
        self.memory = VedaMemory()
        self.brain = VedaBrain()
        self.voice = VedaVoice(self.config)
        self.gui = VedaHUD(self.config, self.process_command)
        self.notif = NotificationModule(self.gui)
        self.router = CommandRouter(self)

        # Initial Connectivity Check
        self._check_links()
        self.brain.ensure_ollama()

    def load_config(self):
        if not os.path.exists("config.json"):
            self.config = {
                "identity": {"name": "Veda", "version": "5.0.0"},
                "preferences": {
                    "appearance": {"transparency": 0.92, "always_on_top": True},
                    "voice": {"online_voice": "en-US-AvaNeural", "wake_word": "hey veda", "offline_rate": 180}
                }
            }
        else:
            with open("config.json", "r") as f:
                self.config = json.load(f)

    def setup_logging(self):
        logging.basicConfig(
            filename="veda.log",
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )

    def _check_links(self):
        def _worker():
            while True:
                # 1. Neural Link
                neural = self.brain.ensure_ollama() is not False
                # 2. Data Link
                try:
                    import requests
                    requests.get("https://google.com", timeout=2)
                    data = True
                except: data = False

                self.gui.after(0, lambda n=neural, d=data: self._update_gui_links(n, d))
                time.sleep(30)

        threading.Thread(target=_worker, daemon=True).start()

    def _update_gui_links(self, neural, data):
        self.gui.links["NEURAL"].configure(text="ACTIVE" if neural else "OFFLINE", text_color="#00d4ff" if neural else "#ff3e3e")
        self.gui.links["DATA"].configure(text="ACTIVE" if data else "OFFLINE", text_color="#00d4ff" if data else "#ff3e3e")
        self.gui.links["VOICE"].configure(text="ACTIVE", text_color="#00d4ff") # Simplified for now

    def process_command(self, user_input):
        logging.info(f"Command Received: {user_input}")

        # Classification
        category = self.brain.classify_intent(user_input)

        response = None
        if category in ["command", "search", "productivity", "calculation"]:
            intent_data = self.brain.extract_params(user_input)
            response = self.router.route(intent_data)

        # Fallback
        if not response:
            history = self.memory.get_context()
            response = self.brain.chat(user_input, history)

        # Logging & State
        self.memory.log_interaction("user", user_input)
        self.memory.log_interaction("assistant", response)

        # UI & Voice
        self.gui.after(0, lambda: self.gui.add_message("Veda", response))
        self.voice.speak(response)

    def run(self):
        self.notif.notify("Interface online. Stark Protocol active.", "VEDA v5.0")
        threading.Thread(target=self.wake_word_loop, daemon=True).start()
        self.gui.start()

    def wake_word_loop(self):
        while True:
            if self.voice.listen_passive():
                self.gui.after(0, lambda: self.gui.add_message("System", "Holographic interface active."))
            time.sleep(0.1)

    def notify(self, message):
        self.notif.notify(message)

if __name__ == "__main__":
    try:
        assistant = VedaAssistant()
        assistant.run()
    except Exception as e:
        print(f"CRITICAL KERNEL ERROR: {e}")
        logging.critical(f"Panic: {e}")
