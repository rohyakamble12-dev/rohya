import requests
import sys
import os
import json
import re
import logging
import threading
import time
from modules.ui import VedaHUD
from modules.voice import VedaVoice
from modules.brain import VedaBrain
from modules.commands import CommandRouter
from modules.memory import VedaMemory
from modules.notifications import NotificationModule
from modules.monitor import MonitorModule

class VedaAssistant:
    def __init__(self):
        self.load_config()
        self.setup_logging()

        # Core Subsystems
        self.memory = VedaMemory()
        self.brain = VedaBrain()
        self.voice = VedaVoice(self.config)
        self.gui = VedaHUD(self.config, self)
        self.notif = NotificationModule(self.gui)
        self.monitor = MonitorModule(self)
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
        self.gui.links["NEURAL"].configure(text="ACTIVE" if neural else "OFFLINE", text_color="#00ffcc" if neural else "#ff3e3e")
        self.gui.links["DATA"].configure(text="ACTIVE" if data else "OFFLINE", text_color="#00ffcc" if data else "#ff3e3e")
        self.gui.links["VOICE"].configure(text="ACTIVE", text_color="#00ffcc")
        self.gui.links["OPTIC"].configure(text="ACTIVE", text_color="#00ffcc") # Assuming system camera is detected

    def process_command(self, user_input):
        logging.info(f"Command Received: {user_input}")

        # Segment multi-commands: "open chrome and then set volume to 50"
        commands = re.split(r'\s+(?:and|then|also|after that)\s+', user_input, flags=re.IGNORECASE)
        final_responses = []

        for cmd in commands:
            cmd = cmd.strip()
            if not cmd: continue

            self.gui.after(0, lambda: self.gui.set_state("thinking"))

            # 1. Survival Mode Check (Direct regex for core commands)
            response = self._handle_survival_mode(cmd)

            if not response:
                # 2. Semantic Intent Path
                category = self.brain.classify_intent(cmd)
                if category in ["command", "search", "productivity", "calculation"]:
                    intent_data = self.brain.extract_params(cmd)
                    response = self.router.route(intent_data)

                    # Tactical Failover: if route failed, ask brain for alternative
                    if not response or "failed" in response.lower() or "not found" in response.lower():
                        history = self.memory.get_context()
                        response = self.brain.chat(f"Command '{cmd}' failed. Suggest an alternative to the operator.", history)

            # 3. Neural Fallback (Conversation)
            if not response:
                history = self.memory.get_context()
                facts = self.memory.search_facts("")
                fact_str = "\n".join(facts) if facts else ""
                response = self.brain.chat(cmd, history, facts=fact_str)

                # Pro-Active Learning: Store user preferences/facts
                if any(t in cmd.lower() for t in ["my name is", "i like", "call me", "remember that"]):
                    self.memory.add_fact(cmd)

            final_responses.append(response)

        # Unified Response Handling
        combined_response = ". ".join([r for r in final_responses if r])
        self.memory.log_interaction("user", user_input)
        self.memory.log_interaction("assistant", combined_response)

        # UI & Voice
        self.gui.after(0, lambda: self.gui.set_state("speaking"))
        self.gui.after(0, lambda: self.gui.add_message("Veda", combined_response))
        self.voice.speak(combined_response)
        self.gui.after(0, lambda: self.gui.set_state("idle"))

    def run(self):
        self.notif.notify("Interface online. Stark Protocol active.", "VEDA v5.0")
        self.monitor.start()
        threading.Thread(target=self.wake_word_loop, daemon=True).start()
        threading.Thread(target=self._metrics_updater, daemon=True).start()
        self.gui.start()

    def _metrics_updater(self):
        while True:
            try:
                import psutil
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                self.gui.after(0, lambda c=cpu, r=ram: self._ui_metrics_sync(c, r))
            except: pass
            time.sleep(2)

    def _ui_metrics_sync(self, cpu, ram):
        if hasattr(self.gui, 'cpu_bar'):
            self.gui.cpu_bar.set(cpu/100)
        if hasattr(self.gui, 'ram_bar'):
            self.gui.ram_bar.set(ram/100)

        # Image-specific labels from cmd.png
        if hasattr(self.gui, 'stats_labels'):
            self.gui.stats_labels["THREADS"].configure(text=str(threading.active_count()))
            # Plugins count - from router
            plugin_count = len([m for m in dir(self.router) if not m.startswith("_")])
            self.gui.stats_labels["PLUGINS"].configure(text=str(plugin_count))

    def _trigger_mic(self):
        self.gui.after(0, lambda: self.gui.add_message("System", "LISTENING..."))
        self.gui.after(0, lambda: self.gui.set_state("speaking")) # Visual feedback
        query = self.voice.listen()
        if query:
            self.gui.after(0, lambda: self.gui.add_message("User", query))
            self.process_command(query)
        self.gui.after(0, lambda: self.gui.set_state("idle"))

    def wake_word_loop(self):
        while True:
            if self.voice.listen_passive():
                self.gui.after(0, lambda: self.gui.add_message("System", "Holographic interface active."))
            time.sleep(0.1)

    def _handle_survival_mode(self, text):
        """Instant offline processing for core intents."""
        text = text.lower().strip()

        # 0. Quick Responses (Survival 4.0)
        if text in ["hello", "hi", "hey", "veda"]:
            return "Systems operational. Standing by for command, Operator."
        if "who are you" in text or "your identity" in text:
            return "I am Veda. Your personal tactical interface and system guardian."
        if "how are you" in text:
            return "My core systems are reporting 100% efficiency. Ready for engagement."
        if "thank you" in text or "thanks" in text:
            return "Of course, Operator. Efficiency is my primary directive."
        if "time" in text and "what" in text:
            return f"Current tactical time is {time.strftime('%H:%M:%S')}."
        if "date" in text and "what" in text:
            return f"Today's date is {time.strftime('%A, %B %d, %Y')}."
        if "active" in text and "window" in text:
            return self.router.system.get_active_window()

        # Remove common wake-word/politeness prefixes
        text = re.sub(r'^(veda|hey veda|please|could you|would you mind|just)\s+', '', text)

        # 1. System Controls
        if "open" in text or "launch" in text:
            app = re.sub(r'.*(open|launch)\s+', '', text).strip()
            return self.router.system.open_app(app)
        if "close" in text:
            app = text.split("close")[-1].strip()
            return self.router.system.close_app(app)
        if "volume" in text:
            match = re.search(r"(\d+)", text)
            level = match.group(1) if match else (0 if "mute" in text else 50)
            return self.router.system.set_volume(level)
        if "brightness" in text:
            match = re.search(r"(\d+)", text)
            level = match.group(1) if match else 50
            return self.router.system.set_brightness(level)

        # 2. File Operations
        if "move" in text:
            # Simple regex: move [src] to [dst]
            match = re.search(r"move\s+(.+)\s+to\s+(.+)", text)
            if match:
                return self.router.system.move_file(match.group(1).strip(), match.group(2).strip())
        if "find" in text or "search for file" in text:
            filename = re.sub(r'.*(find|search for file)\s+', '', text).strip()
            return self.router.files.find_file(filename)

        # 3. Utilities
        if "screenshot" in text or "capture" in text:
            return self.router.system.screenshot()
        if "health" in text or "status" in text:
            return self.router.system.get_health()
        if "lock" in text and "pc" in text:
            return self.router.system.lock_pc()

        return None

    def notify(self, message):
        self.notif.notify(message)
        self.gui.after(0, lambda: self.gui.add_message("System", message))
        if "ALERT" in message:
            self.gui.after(0, lambda: self.gui.set_state("thinking")) # Visual pulse
            self.voice.speak(message)

if __name__ == "__main__":
    try:
        assistant = VedaAssistant()
        assistant.run()
    except Exception as e:
        print(f"CRITICAL KERNEL ERROR: {e}")
        logging.critical(f"Panic: {e}")
