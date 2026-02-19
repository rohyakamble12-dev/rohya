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
from veda.features.translator import VedaTranslator
from veda.features.automation import VedaAutomation
from veda.features.scraper import VedaScraper
from veda.features.task_master import VedaTaskMaster
from veda.core.context import VedaContext
from veda.utils.notifications import VedaNotifications
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
        self.translator = VedaTranslator()
        self.automation = VedaAutomation()
        self.scraper = VedaScraper()
        self.task_master = VedaTaskMaster(self)
        self.context = VedaContext(self)
        self.protocols = VedaProtocols()

        # Start background health monitoring
        self.life.start_routine_monitor()
        # Start background context monitoring
        self.context.start_monitoring()

    def sync_protocols(self):
        """Syncs local protocol state with GUI toggles."""
        self.protocols.protocols["deep_research"] = self.gui.deep_search_var.get()
        self.protocols.protocols["private_mode"] = self.gui.private_var.get()
        self.protocols.protocols["context_monitoring"] = self.gui.context_var.get()

        if self.protocols.protocols["context_monitoring"]:
            self.context.start_monitoring()
        else:
            self.context.stop_monitoring()

    def process_command(self, user_input):
        """Processes a user command, determines intent, and executes actions."""
        self.gui.set_voice_active(True)
        if not user_input or user_input == "None":
            return

        # Ensure protocols are synced before processing
        self.sync_protocols()

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
            if self.protocols.is_allowed("deep_research"):
                topic = params.get("topic", user_input)
                response = self.research.get_summary(topic)
            else:
                response = "Protocol Error: DEEP RESEARCH is currently offline. Please enable it on the HUD."
            action_taken = True
        elif intent == "read_doc":
            if self.protocols.is_allowed("document_learning"):
                path = params.get("path", "")
                response = self.research.read_document(path)
            else:
                response = "Protocol Error: DOCUMENT LEARNING is restricted."
            action_taken = True
        elif intent == "sys_health":
            response = self.diagnostics.get_system_health()
            action_taken = True
        elif intent == "net_info":
            response = self.diagnostics.get_network_info()
            action_taken = True
        elif intent == "play_music":
            song = params.get("song_name", user_input)
            response = self.media.play_song(song)
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
            elif mode == "gaming": response = self.modes.gaming_mode()
            else: response = self.modes.normal_mode()
            action_taken = True
        elif intent == "translate":
            text = params.get("text", user_input)
            lang = params.get("language", "en")
            response = self.translator.translate_text(text, target_lang=lang)
            action_taken = True
        elif intent == "start_recording":
            response = self.automation.start_recording()
            action_taken = True
        elif intent == "stop_recording":
            name = params.get("name", "default")
            response = self.automation.stop_recording(name)
            action_taken = True
        elif intent == "play_macro":
            name = params.get("name", "default")
            response = self.automation.play_macro(name)
            action_taken = True
        elif intent == "ingest_web":
            url = params.get("url", "")
            if url:
                raw_text = self.scraper.ingest_url(url)
                response = self.llm.chat(f"Summarize this web content: {raw_text}")
            else:
                response = "Please provide a valid URL."
            action_taken = True
        elif intent == "todo_add":
            task = params.get("task", user_input)
            response = self.task_master.add_todo(task)
            action_taken = True
        elif intent == "todo_list":
            response = self.task_master.get_todos()
            action_taken = True
        elif intent == "pomodoro":
            mins = params.get("minutes", 25)
            response = self.task_master.start_pomodoro(mins)
            action_taken = True
        elif intent == "define_protocol":
            name = params.get("name", "")
            cmds = params.get("commands", [])
            if name and cmds:
                self.llm.memory.store_custom_protocol(name, cmds)
                response = f"Custom protocol '{name}' established."
            else:
                response = "Protocol definition failed. Need name and commands."
            action_taken = True
        elif intent == "run_protocol":
            name = params.get("name", "")
            cmds = self.llm.memory.get_custom_protocol(name)
            if cmds:
                self.gui.update_chat("Veda", f"Executing protocol: {name}")
                for cmd in cmds:
                    self.process_command(cmd)
                response = f"Protocol '{name}' execution complete."
            else:
                response = f"Protocol '{name}' not found."
            action_taken = True

        # 3. If no specific action or we want a conversational response
        if not action_taken or "none" in intent:
            current_context = self.context.get_current_context() if self.protocols.protocols["context_monitoring"] else None
            # Pass protocol status to LLM
            protocol_status = self.protocols.get_status()
            response = self.llm.chat(user_input, context_info=current_context, protocols=protocol_status)

        # 4. Update UI and Speak
        self.gui.update_chat("Veda", response)
        try:
            self.voice.speak(response)
        except Exception as e:
            print(f"Speech error: {e}")
            self.gui.update_chat("System", "Voice module encountered an error, but I am still processing your requests.")
        finally:
            self.gui.set_voice_active(False)

    def system_alert(self, message):
        """Used for background routine alerts."""
        VedaNotifications.send_toast("Veda System Alert", message)
        self.gui.update_chat("System", message)
        self.voice.speak(message)

    def on_context_change(self, app_name):
        """Called when the user switches applications."""
        suggestions = {
            "Visual Studio Code": "Need documentation or a quick code review?",
            "Chrome": "I can help with web research or summaries.",
            "Notepad": "Shall I save this as a permanent note for you?",
            "Word": "I can help you draft or research content.",
            "Spotify": "Music control is active. You can say 'Next track' or 'Pause'."
        }
        tip = suggestions.get(app_name, f"I'm ready to assist with {app_name}.")
        self.gui.show_suggestion(tip)

    def listen_and_process(self):
        """Listens for voice input and processes it."""
        query = self.voice.listen()
        if query != "None":
            self.gui.update_chat("You", query)
            self.process_command(query)
        self.gui.reset_voice_button()
