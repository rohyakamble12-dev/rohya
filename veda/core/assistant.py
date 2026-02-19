from veda.core.llm import VedaLLM
from veda.core.voice import VedaVoice
from veda.features.system_control import SystemControl
from veda.features.web_info import WebInfo
from veda.features.tools import VedaTools
from veda.features.life import VedaLife
from veda.features.finance import VedaFinance
from veda.features.vision import VedaVision
from veda.features.research import VedaResearch
from veda.features.diagnostics import VedaDiagnostics
from veda.features.media import VedaMedia
from veda.features.file_manager import VedaFileManager
from veda.features.modes import VedaModes
from veda.core.context import VedaContext
from veda.utils.protocols import VedaProtocols

class VedaAssistant:
    def __init__(self, gui):
        self.gui = gui
        self.llm = VedaLLM()
        self.voice = VedaVoice()
        self.system = SystemControl()
        self.web = WebInfo()
        self.tools = VedaTools()
        self.life = VedaLife(self)
        self.finance = VedaFinance()
        self.vision = VedaVision()
        self.research = VedaResearch()
        self.diagnostics = VedaDiagnostics()
        self.media = VedaMedia()
        self.file_manager = VedaFileManager()
        self.modes = VedaModes(self)
        self.context = VedaContext(self)
        self.protocols = VedaProtocols()

        # Start background health monitoring
        self.life.start_routine_monitor()
        # Start background context monitoring
        self.context.start_monitoring()

    def process_command(self, user_input):
        """Processes a user command, determines intent, and executes actions."""
        if not user_input or user_input == "None":
            return

        # Sync protocols with GUI state
        self.protocols.protocols["deep_research"] = self.gui.deep_search_var.get()
        self.protocols.protocols["private_mode"] = self.gui.private_var.get()
        self.protocols.protocols["context_monitoring"] = self.gui.context_var.get()

        # Update monitor state based on toggle
        if self.protocols.protocols["context_monitoring"]:
            self.context.start_monitoring()
        else:
            self.context.stop_monitoring()

        # 1. Extract Intent
        intent_data = self.llm.extract_intent(user_input)
        intent = intent_data.get("intent", "none")
        params = intent_data.get("params", {})

        response = ""
        action_taken = False

        # 2. Execute Feature based on Intent
        if intent == "open_app":
            app = params.get("app_name", "")
            response = self.system.open_app(app)
            action_taken = True
        elif intent == "close_app":
            app = params.get("app_name", "")
            response = self.system.close_app(app)
            action_taken = True
        elif intent == "set_volume":
            level = params.get("level", 50)
            response = self.system.set_volume(level)
            action_taken = True
        elif intent == "set_brightness":
            level = params.get("level", 50)
            response = self.system.set_brightness(level)
            action_taken = True
        elif intent == "web_search":
            query = params.get("query", user_input)
            response = self.web.search(query)
            action_taken = True
        elif intent == "weather":
            city = params.get("city", "auto")
            response = self.web.get_weather(city)
            action_taken = True
        elif intent == "screenshot":
            response = self.system.screenshot()
            action_taken = True
        elif intent == "lock_pc":
            response = self.system.lock_pc()
            action_taken = True
        elif intent == "time":
            response = self.tools.get_time()
            action_taken = True
        elif intent == "date":
            response = self.tools.get_date()
            action_taken = True
        elif intent == "note":
            note_text = params.get("text", user_input)
            response = self.tools.take_note(note_text)
            action_taken = True
        elif intent == "stock_price":
            symbol = params.get("symbol", "")
            response = self.finance.get_market_info(symbol)
            action_taken = True
        elif intent == "crypto_price":
            coin = params.get("coin", "bitcoin")
            response = self.finance.get_crypto_price(coin)
            action_taken = True
        elif intent == "remember_fact":
            key = params.get("key", "")
            value = params.get("value", "")
            self.llm.memory.store_fact(key, value)
            response = f"I'll remember that {key} is {value}."
            action_taken = True
        elif intent == "vision_analyze":
            response = self.vision.analyze_current_view()
            action_taken = True
        elif intent == "motivation":
            response = self.life.get_motivation()
            action_taken = True
        elif intent == "deep_research":
            topic = params.get("topic", user_input)
            response = self.research.get_summary(topic)
            action_taken = True
        elif intent == "read_doc":
            path = params.get("path", "")
            response = self.research.read_document(path)
            action_taken = True
        elif intent == "sys_health":
            response = self.diagnostics.get_system_health()
            action_taken = True
        elif intent == "net_info":
            response = self.diagnostics.get_network_info()
            action_taken = True
        elif intent == "media_control":
            cmd = params.get("command", "play_pause")
            if cmd == "next": response = self.media.next_track()
            elif cmd == "prev": response = self.media.prev_track()
            elif cmd == "stop": response = self.media.stop_media()
            else: response = self.media.play_pause()
            action_taken = True
        elif intent == "file_search":
            name = params.get("filename", "")
            response = self.file_manager.search_file(name)
            action_taken = True
        elif intent == "set_mode":
            mode = params.get("mode", "normal")
            if mode == "focus": response = self.modes.focus_mode()
            elif mode == "stealth": response = self.modes.stealth_mode()
            else: response = self.modes.normal_mode()
            action_taken = True

        # 3. If no specific action or we want a conversational response
        if not action_taken or "none" in intent:
            current_context = self.context.get_current_context() if self.protocols.protocols["context_monitoring"] else None
            response = self.llm.chat(user_input, context_info=current_context)

        # 4. Update UI and Speak
        self.gui.update_chat("Veda", response)
        try:
            self.voice.speak(response)
        except Exception as e:
            print(f"Speech error: {e}")
            self.gui.update_chat("System", "Voice module encountered an error, but I am still processing your requests.")

    def system_alert(self, message):
        """Used for background routine alerts."""
        self.gui.update_chat("System", message)
        self.voice.speak(message)

    def listen_and_process(self):
        """Listens for voice input and processes it."""
        query = self.voice.listen()
        if query != "None":
            self.gui.update_chat("You", query)
            self.process_command(query)
        self.gui.reset_voice_button()
