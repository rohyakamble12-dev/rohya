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

        # Post-init link
        self.brain.ensure_ollama()

    def load_config(self):
        if not os.path.exists("config.json"):
            # Fallback default config
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

    def process_command(self, user_input):
        logging.info(f"User Input: {user_input}")

        # 1. Classify Intent
        category = self.brain.classify_intent(user_input)

        response = None
        if category in ["command", "search", "productivity", "calculation"]:
            # 2. Extract specific intent and params via LLM
            intent_data = self.brain.extract_params(user_input)
            response = self.router.route(intent_data)

        # 3. Fallback to Conversation
        if not response:
            history = self.memory.get_context()
            response = self.brain.chat(user_input, history)

        # 4. Finalize
        self.memory.log_interaction("user", user_input)
        self.memory.log_interaction("assistant", response)

        # Thread-safe UI update
        self.gui.after(0, lambda: self.gui.add_message("Veda", response))

        # Vocalize
        self.voice.speak(response)
        logging.info(f"Veda Response: {response}")

    def run(self):
        self.notif.notify("Systems initialized. Stark Protocol active.", "VEDA ONLINE")
        # Start passive wake word listener in background
        threading.Thread(target=self.wake_word_loop, daemon=True).start()
        self.gui.start()

    def wake_word_loop(self):
        while True:
            if self.voice.listen_passive():
                self.gui.after(0, lambda: self.gui.add_message("System", "Wake word detected."))
                # Future: trigger active listening state
            time.sleep(0.5)

    def notify(self, message):
        self.notif.notify(message)

if __name__ == "__main__":
    try:
        assistant = VedaAssistant()
        assistant.run()
    except Exception as e:
        logging.critical(f"KERNEL PANIC: {e}")
        print(f"CRITICAL ERROR: {e}")
