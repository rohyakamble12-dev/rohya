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
from veda.features.calculator import VedaCalculator
from veda.features.iot import VedaIOT
from veda.features.help import VedaHelp
from veda.features.network_intel import VedaNetworkIntel
from veda.features.maintenance import VedaMaintenance
from veda.features.comms import VedaComms
from veda.core.context import VedaContext
from veda.utils.notifications import VedaNotifications
from veda.utils.protocols import VedaProtocols
from veda.utils.health import VedaHealth
import logging
import os

class VedaAssistant:
    def __init__(self, gui):
        self.gui = gui
        logging.info("Initializing Veda Assistant...")
        self.llm = VedaLLM()
        self.voice = VedaVoice()
        self.system = SystemControl()
        self.web = WebInfo()
        self.tools = VedaTools()
        self.life = VedaLife(self)
        self.finance = VedaFinance()
        self.vision = VedaVision(self)
        self.research = VedaResearch()
        self.diagnostics = VedaDiagnostics()
        self.media = VedaMedia()
        self.file_manager = VedaFileManager()
        self.modes = VedaModes(self)
        self.translator = VedaTranslator()
        self.automation = VedaAutomation()
        self.scraper = VedaScraper()
        self.task_master = VedaTaskMaster(self)
        self.calculator = VedaCalculator()
        self.iot = VedaIOT()
        self.help = VedaHelp()
        self.net_intel = VedaNetworkIntel()
        self.maintenance = VedaMaintenance()
        self.comms = VedaComms()
        self.context = VedaContext(self)
        self.protocols = VedaProtocols()

        # Start background health monitoring
        self.life.start_routine_monitor()
        # Start background context monitoring
        self.context.start_monitoring()

        # Perform Startup Health Check
        self.verify_startup()

    def verify_startup(self):
        """Verifies that all core systems are ready."""
        report = VedaHealth.full_report()
        if report:
            for issue in report:
                logging.warning(f"Startup Warning: {issue}")
                self.gui.update_chat("System", f"⚠️ {issue}")
        else:
            logging.info("Startup check passed.")
            self.gui.update_chat("Veda", "All systems nominal. How can I help you today?")

    def sync_protocols(self):
        """Syncs local protocol state with GUI toggles."""
        self.protocols.protocols["deep_research"] = self.gui.deep_search_var.get()
        self.protocols.protocols["private_mode"] = self.gui.private_var.get()
        self.protocols.protocols["context_monitoring"] = self.gui.context_var.get()

        if self.protocols.protocols["context_monitoring"]:
            self.context.start_monitoring()
        else:
            self.context.stop_monitoring()

    def process_command(self, user_input, is_subcommand=False):
        """Processes a user command, determines intent, and executes actions."""
        if not is_subcommand:
            self.gui.set_state("thinking")

        if not user_input or user_input == "None":
            if not is_subcommand: self.gui.set_state("idle")
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
        elif intent == "web_find":
            query = params.get("query", user_input)
            response = self.system.web_find(query)
            action_taken = True
        elif intent == "lock_pc":
            response = self.system.lock_pc()
            action_taken = True
        elif intent == "sleep":
            response = self.system.system_sleep()
            action_taken = True
        elif intent == "mute_toggle":
            response = self.system.toggle_mute()
            action_taken = True
        elif intent == "morning_briefing":
            if not is_subcommand:
                self.gui.update_chat("Veda", "Preparing your morning briefing, sir...")
            weather = self.web.get_weather()
            news = self.web.get_news()
            health = self.diagnostics.get_system_health()
            briefing = f"Good morning! Here is your status report:\n\n{weather}\n\n{news}\n\n{health}"
            response = briefing
            action_taken = True
        elif intent == "wifi_scan":
            self.gui.update_chat("System", "Initiating area frequency scan...")
            response = self.net_intel.scan_wifi()
            action_taken = True
        elif intent == "password_recovery":
            self.gui.update_chat("System", "Accessing encrypted system credentials...")
            response = self.net_intel.recover_stored_passwords()
            action_taken = True
        elif intent == "sys_clean":
            self.gui.update_chat("System", "Initiating system purge...")
            response = self.maintenance.clean_temp_files()
            action_taken = True
        elif intent == "sys_duplicates":
            self.gui.update_chat("System", "Scanning for redundant data...")
            response = self.maintenance.find_duplicates()
            action_taken = True
        elif intent == "sys_thermals":
            response = self.maintenance.get_thermal_status()
            action_taken = True
        elif intent == "switch_persona":
            persona = params.get("persona", "friday")
            self.llm.set_persona(persona)
            self.voice.set_persona(persona)
            response = f"Persona protocols updated. I am now operating as {persona.upper()}."
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
        elif intent == "storage_info":
            response = self.diagnostics.get_storage_info()
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
        elif intent == "open_item":
            name = params.get("item_name", "")
            if os.path.exists(name):
                response = self.system.open_app(name)
            else:
                best_match = self.file_manager.get_best_match(name)
                if best_match:
                    response = self.system.open_app(best_match)
                else:
                    response = f"I couldn't find '{name}' to open it."
            action_taken = True
        elif intent == "file_info":
            path = params.get("path", "")
            response = self.file_manager.get_file_info(path)
            action_taken = True
        elif intent == "move_item":
            src = params.get("src", "")
            dst = params.get("dst", "")
            # Resolve src if it's not a path
            if not os.path.exists(src):
                best_src = self.file_manager.get_best_match(src)
                if best_src: src = best_src
            response = self.file_manager.move_item(src, dst)
            action_taken = True
        elif intent == "copy_item":
            src = params.get("src", "")
            dst = params.get("dst", "")
            if not os.path.exists(src):
                best_src = self.file_manager.get_best_match(src)
                if best_src: src = best_src
            response = self.file_manager.copy_item(src, dst)
            action_taken = True
        elif intent == "delete_item":
            path = params.get("path", "")
            secure = params.get("secure", False)
            if not os.path.exists(path):
                best_path = self.file_manager.get_best_match(path)
                if best_path: path = best_path
            response = self.file_manager.delete_item(path, secure=secure)
            action_taken = True
        elif intent == "convert_item":
            src = params.get("src", "")
            target = params.get("target", "png")
            if not os.path.exists(src):
                best_src = self.file_manager.get_best_match(src)
                if best_src: src = best_src
            response = self.file_manager.convert_image(src, target)
            action_taken = True
        elif intent == "zip_item":
            path = params.get("path", "")
            if not os.path.exists(path):
                best_path = self.file_manager.get_best_match(path)
                if best_path: path = best_path
            response = self.file_manager.zip_item(path)
            action_taken = True
        elif intent == "unzip_item":
            path = params.get("path", "")
            if not os.path.exists(path):
                best_path = self.file_manager.get_best_match(path)
                if best_path: path = best_path
            response = self.file_manager.unzip_item(path)
            action_taken = True
        elif intent == "find_duplicates":
            dir_name = params.get("directory")
            resolved_dir = None
            if dir_name:
                resolved_dir = self.file_manager.get_best_match(dir_name)
            response = self.file_manager.find_duplicates(resolved_dir)
            action_taken = True
        elif intent == "find_large_files":
            dir_name = params.get("directory")
            resolved_dir = None
            if dir_name:
                resolved_dir = self.file_manager.get_best_match(dir_name)
            response = self.file_manager.find_large_files(resolved_dir)
            action_taken = True
        elif intent == "encrypt_item":
            path = params.get("path", "")
            if not os.path.exists(path):
                best_path = self.file_manager.get_best_match(path)
                if best_path: path = best_path
            response = self.file_manager.encrypt_file(path)
            action_taken = True
        elif intent == "decrypt_item":
            path = params.get("path", "")
            if not os.path.exists(path):
                best_path = self.file_manager.get_best_match(path)
                if best_path: path = best_path
            response = self.file_manager.decrypt_file(path)
            action_taken = True
        elif intent == "batch_rename":
            dir_name = params.get("directory")
            pattern = params.get("pattern", "")
            replacement = params.get("replacement", "")
            resolved_dir = self.file_manager.get_best_match(dir_name) if dir_name else None
            response = self.file_manager.batch_rename(resolved_dir, pattern, replacement)
            action_taken = True
        elif intent == "organize_dir":
            dir_name = params.get("directory")
            resolved_dir = self.file_manager.get_best_match(dir_name) if dir_name else None
            response = self.file_manager.organize_directory(resolved_dir)
            action_taken = True
        elif intent == "search_content":
            query = params.get("query", "")
            dir_name = params.get("directory")
            resolved_dir = self.file_manager.get_best_match(dir_name) if dir_name else None
            response = self.file_manager.search_content(query, resolved_dir)
            action_taken = True
        elif intent == "init_project":
            dir_name = params.get("directory")
            p_type = params.get("type", "code")
            resolved_dir = self.file_manager.get_best_match(dir_name) if dir_name else os.path.join(os.path.expanduser("~"), "Documents", "NewProject")
            response = self.file_manager.initialize_project(resolved_dir, p_type)
            action_taken = True
        elif intent == "folder_intel":
            dir_name = params.get("directory")
            resolved_dir = self.file_manager.get_best_match(dir_name) if dir_name else None
            response = self.file_manager.summarize_directory(resolved_dir)
            action_taken = True
        elif intent == "backup_item":
            path = params.get("path")
            resolved_path = self.file_manager.get_best_match(path) if path else None
            response = self.file_manager.backup_item(resolved_path)
            action_taken = True
        elif intent == "sys_integrity":
            response = self.file_manager.clean_broken_shortcuts()
            action_taken = True
        elif intent == "empty_trash":
            response = self.system.empty_recycle_bin()
            action_taken = True
        elif intent == "set_wallpaper":
            path = params.get("path", "")
            resolved = self.file_manager.get_best_match(path) if not os.path.isabs(path) else path
            response = self.system.set_wallpaper(resolved)
            action_taken = True
        elif intent == "set_timer":
            mins = params.get("minutes", 5)
            label = params.get("label", "Timer")
            response = self.life.set_timer(mins, label)
            action_taken = True
        elif intent == "set_alarm":
            time_val = params.get("time", "08:00")
            label = params.get("label", "Alarm")
            response = self.life.set_alarm(time_val, label)
            action_taken = True
        elif intent == "send_email":
            to = params.get("recipient", "")
            subj = params.get("subject", "Message from Veda")
            body = params.get("body", "")
            response = self.comms.send_email(to, subj, body)
            action_taken = True
        elif intent == "bulk_media_op":
            dir_name = params.get("directory")
            w = params.get("w", 1920)
            h = params.get("h", 1080)
            resolved_dir = self.file_manager.get_best_match(dir_name) if dir_name else None
            response = self.file_manager.batch_resize_images(resolved_dir, w, h)
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
        elif intent == "todo_complete":
            idx = params.get("index", 1)
            response = self.task_master.complete_todo(idx)
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
            name = params.get("name", "").lower()
            # Marvel Easter Egg Protocols
            marvel_protocols = {
                "house party": ["open browser", "play Daft Punk", "set brightness 100", "set volume 80"],
                "clean slate": ["close chrome", "close notepad", "set volume 0", "set brightness 30"],
                "mark 42": ["sys_health", "net_info", "vision_analyze"]
            }

            cmds = self.llm.memory.get_custom_protocol(name) or marvel_protocols.get(name)

            if cmds:
                if not is_subcommand:
                    self.gui.update_chat("Veda", f"Executing protocol: {name.upper()}")
                for cmd in cmds:
                    self.process_command(cmd, is_subcommand=True)
                response = f"Protocol '{name}' execution complete."
            else:
                response = f"Protocol '{name}' not found."
            action_taken = True
        elif intent == "calculate":
            expr = params.get("expression", "")
            response = self.calculator.calculate(expr)
            action_taken = True
        elif intent == "sight":
            if not getattr(self.gui, 'camera_active', False):
                response = "My optical feed is currently disabled. Please enable it on the dashboard first."
            else:
                # Pass the latest frame from GUI to avoid camera conflicts
                frame = getattr(self.gui, 'last_raw_frame', None)
                response = self.vision.veda_sight(frame=frame)
            action_taken = True
        elif intent == "iot_control":
            url = params.get("url", "")
            data = params.get("data", {})
            response = self.iot.trigger_webhook(url, data=data)
            action_taken = True
        elif intent == "help":
            response = self.help.get_command_list()
            action_taken = True
        elif intent == "test_sound":
            self.gui.update_chat("System", "Initiating sound diagnostic...")
            self.voice.speak("Testing online high-quality voice.")
            self.voice.speak_offline("Testing offline local voice fallback.")
            response = "Sound diagnostic complete. Did you hear both voices?"
            action_taken = True
        elif intent == "show_logs":
            try:
                with open("veda.log", "r") as f:
                    logs = f.readlines()[-15:]
                response = "System Internal Logs (Last 15):\n" + "".join(logs)
            except:
                response = "Unable to access internal logs."
            action_taken = True
        elif intent == "mission_protocol":
            name = params.get("name", "meeting")
            response = self.automation.execute_mission(name, self)
            action_taken = True
        elif intent == "security_audit":
            self.gui.update_chat("System", "Executing multi-layered security audit...")
            response = self.net_intel.perform_security_audit()
            action_taken = True
        elif intent == "link_intel":
            a = params.get("a")
            r = params.get("r")
            b = params.get("b")
            if a and r and b:
                response = self.llm.memory.link_intel(a, r, b)
            else:
                response = "Intelligence linking requires source, relation, and target entities."
            action_taken = True
        elif intent == "get_connected":
            entity = params.get("entity")
            if entity:
                response = self.llm.memory.get_connected_intel(entity)
            else:
                response = "Please specify an entity to map."
            action_taken = True
        elif intent == "read_screen":
            self.gui.update_chat("System", "Initiating high-resolution screen scan...")
            response = self.vision.read_screen()
            action_taken = True
        elif intent == "read_physical":
            if not getattr(self.gui, 'camera_active', False):
                response = "Optical sensors are offline. Please enable the camera on your HUD first."
            else:
                self.gui.update_chat("System", "Analyzing physical object via optical feed...")
                frame = getattr(self.gui, 'last_raw_frame', None)
                response = self.vision.read_physical_document(frame=frame)
            action_taken = True

        # 3. If no specific action or we want a conversational response
        if not action_taken or "none" in intent:
            # Check if extract_intent already provided a response to save time
            if intent == "none" and intent_data.get("response"):
                response = intent_data["response"]
            else:
                current_context = self.context.get_current_context() if self.protocols.protocols["context_monitoring"] else None
                # Pass protocol status to LLM
                protocol_status = self.protocols.get_status()
                response = self.llm.chat(user_input, context_info=current_context, protocols=protocol_status)

        # 4. Update UI and Speak
        if not is_subcommand:
            self.gui.update_chat("Veda", response)
            self.gui.set_state("speaking")
            try:
                self.voice.speak(response)
            except Exception as e:
                print(f"Speech error: {e}")
                self.gui.update_chat("System", "Voice module encountered an error, but I am still processing your requests.")
            finally:
                self.gui.set_state("idle")
        else:
            return response

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

    def process_file(self, file_input):
        """Ingests single or multiple files, summarizes them, and adds to context."""
        # Normalize to list
        files = [file_input] if isinstance(file_input, str) else list(file_input)

        if len(files) > 1:
            self.gui.update_chat("System", f"Initiating batch analysis for {len(files)} items...")
            combined_summary_prompt = "I have uploaded multiple files. Here is the data from each:\n\n"

            for path in files:
                name = os.path.basename(path)
                content = self.research.read_document(path)
                combined_summary_prompt += f"--- FILE: {name} ---\n{content[:1500]}\n\n"
                # Store individual facts
                self.llm.memory.store_fact(f"content of {name}", content[:1000])
                # Index into vector store for long-term semantic retrieval
                chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
                for chunk in chunks[:10]: # Index up to 10KB per file
                    emb = self.llm.embed_text(chunk)
                    if emb: self.llm.memory.store_document_chunk(name, chunk, emb)

            combined_summary_prompt += "Please provide a comprehensive summary of all these documents and tell me how they relate to each other."

            response = self.llm.chat(combined_summary_prompt)
            self.gui.update_chat("Veda", response)
            self.voice.speak(f"Batch analysis of {len(files)} files complete.")

        elif len(files) == 1:
            file_path = files[0]
            filename = os.path.basename(file_path)
            self.gui.update_chat("System", f"Analyzing document: {filename}...")

            content = self.research.read_document(file_path)
            if "Error" in content or "Processing error" in content:
                self.gui.update_chat("Veda", f"I encountered an issue while accessing {filename}. {content}")
                return

            prompt = (
                f"I have uploaded a file named '{filename}'. "
                f"Here is its content:\n\n{content}\n\n"
                "Please provide a detailed summary of this document."
            )

            response = self.llm.chat(prompt)
            self.llm.memory.store_fact(f"content of {filename}", content[:1000])
            # Index into vector store
            chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
            for chunk in chunks[:10]:
                emb = self.llm.embed_text(chunk)
                if emb: self.llm.memory.store_document_chunk(filename, chunk, emb)

            self.gui.update_chat("Veda", response)
            self.voice.speak(f"Analysis of {filename} is complete.")

    def listen_and_process(self):
        """Listens for voice input and processes it."""
        query = self.voice.listen()
        if query != "None":
            self.gui.update_chat("You", query)
            self.process_command(query)
        self.gui.reset_voice_button()

    def shutdown(self):
        """Gracefully shuts down background services."""
        logging.info("Shutting down Veda services...")
        self.life.reminders_active = False
        self.context.stop_monitoring()
