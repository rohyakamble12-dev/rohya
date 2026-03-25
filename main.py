import requests
import sys
import os
import json
import re
import logging
import threading
import time
import socket
import psutil
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
                # 2. Data Link (Using low-level socket for high efficiency)
                try:
                    socket.create_connection(("1.1.1.1", 53), timeout=2)
                    data = True
                except: data = False

                self.gui.after(0, lambda n=neural, d=data: self._update_gui_links(n, d))
                time.sleep(30)

        threading.Thread(target=_worker, daemon=True).start()

    def _update_gui_links(self, neural, data):
        self.gui.sidebar.links["NEURAL"].configure(text="ACTIVE" if neural else "OFFLINE", text_color="#00ffcc" if neural else "#ff3e3e")
        self.gui.sidebar.links["DATA"].configure(text="ACTIVE" if data else "OFFLINE", text_color="#00ffcc" if data else "#ff3e3e")
        self.gui.sidebar.links["VOICE"].configure(text="ACTIVE", text_color="#00ffcc")
        self.gui.sidebar.links["OPTIC"].configure(text="ACTIVE", text_color="#00ffcc")

    def process_command(self, user_input):
        logging.info(f"Command Received: {user_input}")

        # 1. Quick Global Response Check
        survival = self._handle_survival_mode(user_input)
        if survival:
            self._finalize_interaction(user_input, survival)
            return

        # 2. Neural Strategic Planning
        self.gui.after(0, lambda: self.gui.set_state("thinking"))
        raw_plan = self.brain.plan_tactical_steps(user_input)

        # Extract Reasoning (Thought)
        if "<reasoning>" in str(raw_plan):
            match = re.search(r'<reasoning>(.*?)</reasoning>', str(raw_plan), re.DOTALL)
            if match: self.gui.after(0, lambda m=match.group(1): self.gui.add_message("Thought", m))

        # Extract Action List
        plan = []
        if isinstance(raw_plan, list): plan = raw_plan
        else:
            j_match = re.search(r'\[.*\]', str(raw_plan), re.DOTALL)
            if j_match: plan = json.loads(j_match.group())

        final_responses = []
        for step in plan:
            intent = step.get("intent", "none")
            if intent == "none": continue

            res = self.router.route(step)

            # 2.5 Reflection: If step failed, analyze why
            if not res or "failed" in str(res).lower() or "not found" in str(res).lower():
                reflection = self.brain.chat(f"Tactical analysis: Command '{intent}' with params {step.get('params')} failed. Result: {res}. Inform the operator.", [])
                final_responses.append(reflection)
            elif res:
                final_responses.append(res)

        # 3. Handle Remaining / Conversational Needs
        if not final_responses:
            history = self.memory.get_context()
            facts = self.memory.search_facts("")
            screen_ctx = self.memory.load_state("screen_context", "")
            if screen_ctx: facts.append(f"CURRENT SCREEN DATA: {screen_ctx}")

            fact_str = "\n".join(facts)
            stream = self.brain.chat(user_input, history, facts=fact_str, stream=True)

            full_text = ""; lbl = self.gui.add_message("Veda", "...")
            for chunk in stream:
                content = chunk['message']['content']
                full_text += content
                self.gui.after(0, lambda t=full_text, l=lbl: l.configure(text=f"VEDA: {t}"))
            final_responses.append(full_text)

            # Learning
            if any(t in user_input.lower() for t in ["my name is", "i like", "call me"]):
                self.memory.add_fact(user_input)

        combined = ". ".join([r for r in final_responses if r])
        self._finalize_interaction(user_input, combined)

    def _finalize_interaction(self, user_input, response):
        self.memory.log_interaction("user", user_input)
        self.memory.log_interaction("assistant", response)
        self.gui.after(0, lambda: self.gui.set_state("speaking"))
        # If response was not streamed, add it now
        if not any(role in response for role in ["VEDA:", "Veda:"]):
            self.gui.after(0, lambda: self.gui.add_message("Veda", response))
        self.voice.speak(response)
        self.gui.after(0, lambda: self.gui.set_state("idle"))

    def run(self):
        self.notif.notify("Interface online. Stark Protocol active.", "VEDA v5.0")
        self.monitor.start()
        threading.Thread(target=self.wake_word_loop, daemon=True).start()
        threading.Thread(target=self._metrics_updater, daemon=True).start()
        threading.Thread(target=self._optical_feed_loop, daemon=True).start()
        self.gui.start()

    def _optical_feed_loop(self):
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while True:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.gui.after(0, lambda f=frame: self.gui.update_camera(f))
            time.sleep(0.04) # ~25 FPS

    def _metrics_updater(self):
        while True:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                self.gui.after(0, lambda c=cpu, r=ram: self._ui_metrics_sync(c, r))
            except: pass
            time.sleep(2)

    def _ui_metrics_sync(self, cpu, ram):
        if hasattr(self.gui.sidebar, 'cpu_bar'):
            self.gui.sidebar.cpu_bar.set(cpu/100)
        if hasattr(self.gui.sidebar, 'ram_bar'):
            self.gui.sidebar.ram_bar.set(ram/100)

        if hasattr(self.gui.sidebar, 'stats_labels'):
            self.gui.sidebar.stats_labels["THREADS"].configure(text=str(threading.active_count()))
            plugin_count = len([m for m in dir(self.router) if not m.startswith("_")])
            self.gui.sidebar.stats_labels["PLUGINS"].configure(text=str(plugin_count))

    def _trigger_mic(self):
        self.gui.after(0, lambda: self.gui.add_message("System", "LISTENING..."))
        self.gui.after(0, lambda: self.gui.set_state("speaking")) # Visual feedback

        # Start visualization thread
        self._mic_viz_active = True
        threading.Thread(target=self._mic_viz_loop, daemon=True).start()

        query = self.voice.listen()
        self._mic_viz_active = False

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
        """Instant offline processing for core intents (Survival 9.0)."""
        text = text.lower().strip()

        # Adaptive & Fuzzy Rule Check
        rule = self.memory.get_rule(text)
        if rule: return self.router.route(rule)

        # Quick Responses (Omni-Router Fast Path)
        responses = {
            "hello": "Systems operational. Standing by, Operator.",
            "who are you": "I am Veda. Your personal tactical interface and system guardian.",
            "how are you": "Systems reporting 100% efficiency.",
            "thank you": "Efficiency is my primary directive.",
            "system report": self.router.system.get_sys_info(),
            "network status": self.router.system.get_network_info(),
            "shutdown": self.router.system.open_app("shutdown /s /t 60"),
            "restart": self.router.system.open_app("shutdown /r /t 60"),
            "battery": self.router.system.get_health(),
            "active window": self.router.system.get_active_window()
        }
        for trigger, resp in responses.items():
            if trigger == text or (trigger in text and len(text) < 15): return resp

        # Utilities
        if "time" in text: return f"Current tactical time is {time.strftime('%H:%M:%S')}."
        if "date" in text: return f"Today is {time.strftime('%A, %B %d, %Y')}."
        if re.match(r'^[0-9+\-*/().\s^]+$', text) and len(text) > 1:
            try: return f"Calculation: {eval(text, {'__builtins__': None}, {})}."
            except: pass

        # Prefix Cleanup
        text = re.sub(r'^(veda|hey veda|please|could you|would you mind|just)\s+', '', text)

        # Fast Routing
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

    def _mic_viz_loop(self):
        try:
            import pyaudio
            import numpy as np

            # Use same rate as voice.py for efficiency
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
            while self._mic_viz_active:
                data = np.frombuffer(stream.read(1024, exception_on_overflow=False), dtype=np.int16)
                peak = np.abs(data).max() / 32768.0
                self.gui.mic_level = peak
            stream.stop_stream(); stream.close(); p.terminate()
        except: pass

if __name__ == "__main__":
    try:
        assistant = VedaAssistant()
        assistant.run()
    except Exception as e:
        print(f"CRITICAL KERNEL ERROR: {e}")
        logging.critical(f"Panic: {e}")
