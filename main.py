try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
import sys
import os
import json
import re
import logging
import threading
import time
import socket
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
import queue
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

from unittest.mock import MagicMock

# Tactical Module Imports
# Tactical Module Imports (Internal modules are safe to import normally as they guard their own deps)
try:
    from modules.ui import VedaHUD
    from modules.voice import VedaVoice
    from modules.brain import VedaBrain
    from modules.commands import CommandRouter
    from modules.memory import VedaMemory
    from modules.notifications import NotificationModule
    from modules.monitor import MonitorModule
except Exception as e:
    print(f"CRITICAL KERNEL LINK FAILURE: {e}")
    # We proceed if it's just a display issue for headless diagnostics
    if "DISPLAY" not in str(e):
        # If it's a code error in a module, we should see it
        import traceback
        traceback.print_exc()

class VedaAssistant:
    def __init__(self):
        self.setup_logging()
        logging.info("--- VEDA SOVEREIGN KERNEL BOOT ---")
        self._audit_dependencies()

        # Kernel State
        self.command_lock = threading.RLock()
        self.optical_active = False
        self.load_config()

        # 1. Memory Sector
        self.memory = VedaMemory()

        # 2. Neural Link
        self.brain = VedaBrain()
        self.brain.ensure_ollama()

        # 3. HUD and Interface
        self.gui = VedaHUD(self.config, self)
        self.voice = VedaVoice(self.config)
        self.notif = NotificationModule(self.gui)

        # 4. Command Engine
        self.router = CommandRouter(self)
        self.monitor = MonitorModule(self)

        # 5. Start Passive Loops
        self._initialize_subsystems()

    def _initialize_subsystems(self):
        threading.Thread(target=self._preflight_check_loop, name="PreflightThread", daemon=True).start()
        threading.Thread(target=self.wake_word_loop, name="VoiceThread", daemon=True).start()
        threading.Thread(target=self._metrics_updater, name="MetricsThread", daemon=True).start()
        threading.Thread(target=self._optical_feed_loop, name="OpticThread", daemon=True).start()
        threading.Thread(target=self._start_web_hud, name="WebHUDThread", daemon=True).start()
        threading.Thread(target=self._setup_tray, name="TrayThread", daemon=True).start()

        # Guard monitor start (might fail if psutil is crippled)
        try: self.monitor.start()
        except: pass

    def _setup_tray(self):
        """Persistent Tray Icon for Veda."""
        try:
            import pystray
            from PIL import Image
            def on_unload(): self.gui.destroy()
            icon = pystray.Icon("Veda", Image.new('RGB', (64, 64), color=(0, 255, 204)), "Veda Sovereign",
                                menu=pystray.Menu(pystray.MenuItem("Unload Kernel", on_unload)))
            icon.run()
        except: pass

    def _start_web_hud(self):
        """Launches a secondary web interface for remote monitoring."""
        try:
            from flask import Flask, jsonify
            app = Flask(__name__)

            @app.route('/status')
            def status():
                return jsonify({
                    "id": self.config["identity"]["active_id"],
                    "health": self.router.system.get_health(),
                    "network": self.router.system.get_network_info()
                })

            app.run(host="0.0.0.0", port=5000)
        except ImportError:
            logging.error("Web-HUD link failed: Flask missing.")

    def setup_logging(self):
        logging.basicConfig(
            filename="veda.log",
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )
        # Also print to console for visibility since user says files won't load
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logging.getLogger('').addHandler(console)

    def _audit_dependencies(self):
        """Checks for critical and optional modules to provide actionable feedback."""
        essential = ["customtkinter", "ollama", "requests", "cv2", "psutil"]
        missing = []
        for mod in essential:
            try: __import__(mod)
            except ImportError: missing.append(mod)

        if missing:
            logging.warning(f"[SYSTEM ALERT]: Missing tactical modules: {', '.join(missing)}")
            logging.warning("[ADVICE]: Run 'repair_veda.bat' to re-establish system links.")

    def load_config(self):
        if not os.path.exists("config.json"):
            self.config = {
                "identity": {"name": "Veda", "version": "6.0.0", "active_id": "FRIDAY"},
                "operator": {"home": "New York", "work": "Manhattan"},
                "preferences": {
                    "appearance": {"transparency": 0.92, "always_on_top": True},
                    "voice": {"online_voice": "en-US-AvaNeural", "wake_word": "hey veda", "offline_rate": 180}
                }
            }
        else:
            with open("config.json", "r") as f:
                self.config = json.load(f)

    def _preflight_check_loop(self):
        logging.info("[SYSTEM]: Tactical link synchronization active.")
        while True:
            try:
                neural = self.brain.ensure_ollama()
                try:
                    socket.create_connection(("1.1.1.1", 53), timeout=2)
                    data = True
                except: data = False
                self.gui.after(0, lambda n=neural, d=data: self._update_telemetry_ui(n, d))
            except: pass
            time.sleep(30)

    def _update_telemetry_ui(self, neural, data):
        try:
            self.gui.sidebar.links["NEURAL"].configure(text="ACTIVE" if neural else "OFFLINE", text_color="#00ffcc" if neural else "#ff3e3e")
            self.gui.sidebar.links["DATA"].configure(text="ACTIVE" if data else "OFFLINE", text_color="#00ffcc" if data else "#ff3e3e")
            self.gui.sidebar.links["VOICE"].configure(text="ACTIVE", text_color="#00ffcc")
            self.gui.sidebar.links["OPTIC"].configure(text="ACTIVE" if self.optical_active else "OFFLINE", text_color="#00ffcc" if self.optical_active else "#666666")
        except: pass

    def process_command(self, user_input):
        if not user_input: return

        # Immediate UI Feedback
        self.gui.after(0, lambda: self.gui.set_state("thinking"))
        self.gui.after(0, lambda: self.gui.log.status_label.configure(text=f"EXECUTING: {user_input.upper()[:20]}..."))

        with self.command_lock:
            logging.info(f"Input: {user_input}")

            # 1. Resilient Fast-Path (Survival Mode 11.0)
            try:
                survival = self._handle_survival_mode(user_input)
                if survival:
                    self._finalize_interaction(user_input, survival)
                    return
            except Exception as e:
                logging.error(f"Survival error: {e}")

            # 2. Neural Planning
            self.gui.after(0, lambda: self.gui.set_state("thinking"))
            final_responses = []
            try:
                raw_plan = self.brain.plan_tactical_steps(user_input)

                # Thought Visualization
                if "<reasoning>" in str(raw_plan):
                    match = re.search(r'<reasoning>(.*?)</reasoning>', str(raw_plan), re.DOTALL)
                    if match: self.gui.after(0, lambda m=match.group(1): self.gui.add_message("Thought", m))

                # Plan Parsing
                plan = []
                if isinstance(raw_plan, list): plan = raw_plan
                else:
                    j_match = re.search(r'\[.*\]', str(raw_plan), re.DOTALL)
                    if j_match: plan = json.loads(j_match.group())

                for step in plan:
                    intent = step.get("intent", "none")
                    if intent == "none": continue
                    res = self.router.route(step)
                    if res: final_responses.append(res)
            except Exception as e:
                logging.error(f"Planning failure: {e}")
                final_responses = ["Strategic planning interrupted. Reverting to neural fallback."]

            # 3. Neural Fallback / Conversation
            if not final_responses:
                try:
                    history = self.memory.get_context()

                    # RAG Knowledge Retrieval
                    knowledge = self.memory.search_knowledge(user_input)
                    facts = "\n".join(self.memory.search_facts(""))
                    if knowledge: facts += "\nSOVEREIGN KNOWLEDGE:\n" + "\n".join(knowledge)

                    # Active Screen Context Integration
                    screen_ctx = self.memory.load_state("screen_context", "")
                    if any(k in user_input.lower() for k in ["on my screen", "this screen", "what am i looking at"]):
                        real_time_ocr = self.router.vision.screen_ocr()
                        screen_ctx = real_time_ocr

                    if screen_ctx: facts += f"\nSCREEN CONTEXT: {screen_ctx}"

                    stream = self.brain.chat(user_input, history, facts=facts, stream=True)
                    token_queue = queue.Queue()
                    lbl = self.gui.add_message("Veda", "...")

                    def _stream_to_ui():
                        full_text = ""
                        while True:
                            try:
                                token = token_queue.get(timeout=5)
                                if token is None: break
                                full_text += token
                                self.gui.after(0, lambda t=full_text, l=lbl: l.configure(text=f"VEDA: {t}"))
                            except queue.Empty: break

                    threading.Thread(target=_stream_to_ui, daemon=True).start()

                    final_text = ""
                    for chunk in stream:
                        content = chunk['message']['content']
                        final_text += content
                        token_queue.put(content)
                    token_queue.put(None)
                    final_responses.append(final_text)

                    # Pro-Active Learning
                    if any(t in user_input.lower() for t in ["my name is", "i like", "call me"]):
                        self.memory.add_fact(user_input)
                except Exception as e:
                    logging.error(f"Fallback failure: {e}")
                    final_responses.append("Neural link unstable. Core functions only.")

            combined = ". ".join([str(r) for r in final_responses if r])

        # Speak and Finalize outside the lock to keep the kernel responsive
        self._finalize_interaction(user_input, combined)

    def _finalize_interaction(self, user_input, response):
        if not response: return
        self.memory.log_interaction("user", user_input)
        self.memory.log_interaction("assistant", str(response))
        self.gui.after(0, lambda: self.gui.set_state("speaking"))

        if not any(tag in str(response) for tag in ["VEDA:", "Veda:"]):
            self.gui.after(0, lambda: self.gui.add_message("Veda", str(response)))

        self.voice.speak(str(response))
        self.gui.after(0, lambda: self.gui.set_state("idle"))

    def _handle_survival_mode(self, text):
        raw_text = text.lower().strip()

        # Identity Switch Natural Language
        if "switch to jarvis" in raw_text or "activate jarvis" in raw_text:
            return self.switch_identity("JARVIS")
        if "switch to friday" in raw_text or "activate friday" in raw_text:
            return self.switch_identity("FRIDAY")

        # Adaptive Rule Check
        rule = self.memory.get_rule(raw_text)
        if rule: return self.router.route(rule)

        # Identity / Greetings
        if raw_text in ["hello", "hi", "veda", "friday", "hey veda", "hey friday"]:
            return "Systems operational, Operator. Awaiting instructions."
        if "who are you" in raw_text: return "I am Veda. Your personal digital interface and system navigator."

        # Reports & Telemetry
        if any(k in raw_text for k in ["system report", "status report", "telemetry"]):
            return self.router.system.get_sys_info(self)
        if any(k in raw_text for k in ["battery", "health", "integrity"]):
            return self.router.system.get_health()
        if "network" in raw_text and "info" in raw_text:
            return self.router.system.get_network_info()

        # Prefix Scrubbing for Command Extraction
        text = re.sub(r'^(veda|hey veda|friday|hey friday|please|could you|i need you to|can you)\s+', '', raw_text)

        # Math Fast-Path (Now after prefix scrubbing)
        if re.match(r'^[0-9+\-*/().\s^]+$', text) and len(text) > 1:
            try: return f"Calculation result: {eval(text, {'__builtins__': None}, {})}."
            except: pass

        # OS Control Fast-Paths (Survival Override)
        # --- Launch/Open ---
        if text.startswith(("open ", "launch ", "start ")):
            app = re.sub(r'^(open|launch|start)\s+', '', text).strip()
            return self.router.route({"intent": "open_app", "params": {"app_name": app}})

        # --- Close/Terminate ---
        if text == "close all":
            return self.router.protocols.clean_slate()

        if text.startswith(("close ", "exit ", "terminate ", "kill ", "stop ")):
            app = re.sub(r'^(close|exit|terminate|kill|stop)\s+', '', text).strip()
            if app == "all": return self.router.protocols.clean_slate()
            return self.router.route({"intent": "close_app", "params": {"app_name": app}})

        # --- Volume Controls ---
        if "volume" in text:
            vol_match = re.search(r'(\d+)', text)
            if vol_match:
                return self.router.route({"intent": "set_volume", "params": {"level": int(vol_match.group(1))}})
            if "mute" in text or "zero" in text:
                return self.router.route({"intent": "set_volume", "params": {"level": 0}})
            if "max" in text:
                return self.router.route({"intent": "set_volume", "params": {"level": 100}})

        # --- Brightness ---
        if "brightness" in text:
            bri_match = re.search(r'(\d+)', text)
            if bri_match:
                return self.router.route({"intent": "set_brightness", "params": {"level": int(bri_match.group(1))}})

        # --- File Searching ---
        if text.startswith(("find ", "search for ", "locate ")):
            query = re.sub(r'^(find|search for|locate)\s+', '', text).strip()
            if not any(k in query for k in ["on web", "google", "online"]):
                return self.router.route({"intent": "file_find", "params": {"filename": query}})

        # --- System Commands ---
        if text in ["screenshot", "take a screenshot", "capture screen"]:
            return self.router.route({"intent": "screenshot"})
        if text in ["lock", "lock pc", "lock computer"]:
            return self.router.route({"intent": "lock_pc"})

        return None

    def switch_identity(self, name):
        name = name.upper()
        if name not in ["JARVIS", "FRIDAY"]: return "Identity not recognized."

        # Voiceprint Simulation Step
        self.gui.after(0, lambda: self.gui.add_message("System", f"ANALYZING VOICEPRINT FOR {name} ACCESS..."))
        time.sleep(1.5)

        self.brain.switch_identity(name)
        res = self.voice.switch_identity(name)
        self.config["identity"]["active_id"] = name
        with open("config.json", "w") as f: json.dump(self.config, f)
        return f"VOICEPRINT VERIFIED. {res}"

    def hot_reload(self):
        """Re-initializes all tactical modules without a kernel restart."""
        import importlib
        try:
            for module_name in ["modules.ui", "modules.voice", "modules.brain", "modules.commands", "modules.memory", "modules.system", "modules.files", "modules.intel", "modules.media", "modules.productivity", "modules.vision", "modules.comms", "modules.automation", "modules.protocols"]:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])

            # Re-link the router and components
            self.router = sys.modules["modules.commands"].CommandRouter(self)
            return "ULTRON: Tactical modules hot-reloaded. System links synchronized."
        except Exception as e:
            return f"ULTRON: Hot-reload protocol failed: {e}"

    def toggle_camera(self):
        self.optical_active = not self.optical_active
        return f"Optic link {'established' if self.optical_active else 'severed'}."

    def run(self):
        # 1. Dynamic Greeting Sequence
        threading.Thread(target=self._initial_greeting, daemon=True).start()
        # 2. Launch Interface
        self.gui.start()

    def _initial_greeting(self):
        self.voice.play_sfx("startup")
        time.sleep(2) # Give UI a moment to load

        # Biometric Authentication Step
        self.gui.after(0, lambda: self.gui.add_message("System", "INITIATING STARTUP BIOMETRIC SCAN..."))
        self.voice.play_sfx("scan")
        auth = self.router.vision.security_perimeter_scan()
        self.gui.after(0, lambda: self.gui.add_message("System", auth))
        self.voice.play_sfx("success")

        hour = time.localtime().tm_hour
        period = "morning" if 5 <= hour < 12 else "afternoon" if 12 <= hour < 18 else "evening"

        name = "Sir" if self.config["identity"]["active_id"] == "JARVIS" else "Operator"

        # Operator State Integration
        state = self.router.vision.analyze_operator_state()
        mood = state.split("appears ")[1].split(".")[0] if "appears " in state else "NOMINAL"

        greeting = f"Good {period}, {name}. Systems are operational. Mood analysis: {mood}. Awaiting tactical instructions."

        self.gui.after(0, lambda: self.gui.add_message("Veda", greeting))
        self.voice.speak(greeting)

    def _optical_feed_loop(self):
        if not HAS_CV2: return
        cap = None
        last_gesture_time = 0
        while True:
            if self.optical_active:
                if cap is None: cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.gui.after(0, lambda f=frame_rgb: self.gui.update_camera(f))

                    # Gesture Processing (Stark Interface)
                    if time.time() - last_gesture_time > 1.0:
                        gesture = self.router.vision.detect_gesture(frame_rgb)
                        if gesture:
                            self._handle_hand_gesture(gesture)
                            last_gesture_time = time.time()
            else:
                if cap is not None:
                    cap.release(); cap = None
                    self.gui.after(0, lambda: self.gui.sidebar.cam_label.configure(image="", text="OFFLINE"))
            time.sleep(0.04)

    def _metrics_updater(self):
        while True:
            try:
                if HAS_PSUTIL:
                    cpu = psutil.cpu_percent()
                    ram = psutil.virtual_memory().percent
                    self.gui.after(0, lambda c=cpu, r=ram: self._ui_metrics_sync(c, r))
            except: pass
            time.sleep(2)

    def _handle_hand_gesture(self, gesture):
        if gesture == "MUTE":
            self.process_command("set volume 0")
            self.notify("STARK INTERFACE: Audio output MUTED via manual gesture.")
        elif gesture == "VOL_UP":
            self.process_command("set volume 80")
            self.notify("STARK INTERFACE: Audio gain INCREASED via manual gesture.")
        elif gesture == "VOL_DOWN":
            self.process_command("set volume 20")
            self.notify("STARK INTERFACE: Audio gain REDUCED via manual gesture.")

    def _ui_metrics_sync(self, cpu, ram):
        try:
            self.gui.sidebar.cpu_bar.set(cpu/100)
            self.gui.sidebar.ram_bar.set(ram/100)
            self.gui.sidebar.stats_labels["THREADS"].configure(text=str(threading.active_count()))
            self.gui.sidebar.stats_labels["PLUGINS"].configure(text=str(len([m for m in dir(self.router) if not m.startswith("_")])))
        except: pass

    def _trigger_mic(self):
        def _mic_thread():
            self.gui.after(0, lambda: self.gui.add_message("System", "LISTENING..."))
            query = self.voice.listen()
            if query:
                self.gui.after(0, lambda: self.gui.add_message("User", query))
                self.process_command(query)
        threading.Thread(target=_mic_thread, daemon=True).start()

    def process_command_async(self, command):
        """Standard entry point for UI/threaded commands to prevent blocking."""
        threading.Thread(target=self.process_command, args=(command,), daemon=True).start()

    def wake_word_loop(self):
        while True:
            if self.voice.listen_passive():
                self.gui.after(0, lambda: self.gui.add_message("System", "Holographic interface active."))
            time.sleep(0.1)

    def notify(self, message):
        self.notif.notify(message)
        self.gui.after(0, lambda: self.gui.add_message("System", message))
        if "ALERT" in message: self.voice.speak(message)

if __name__ == "__main__":
    try:
        assistant = VedaAssistant()
        assistant.run()
    except Exception as e:
        print(f"CRITICAL KERNEL ERROR: {e}")
        logging.critical(f"Panic: {e}")
