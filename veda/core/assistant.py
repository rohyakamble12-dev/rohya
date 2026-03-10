from veda.core.llm import VedaLLM
from veda.core.voice import VedaVoice
from veda.core.planner import TacticalFastPath
from veda.core.memory import VedaMemory
from veda.utils.sanitizer import VedaSanitizer
from veda.features.system_control import SystemControl
from veda.features.web_info import WebInfo
from veda.features.tools import VedaTools
from veda.features.tasks import TaskManager
from veda.features.modes import ModeManager

class VedaAssistant:
    def __init__(self, gui):
        self.gui = gui
        self.memory = VedaMemory()
        self.llm = VedaLLM()
        self.voice = VedaVoice()
        self.planner = TacticalFastPath()
        self.system = SystemControl()
        self.web = WebInfo()
        self.tools = VedaTools()
        self.tasks = TaskManager()
        self.modes = ModeManager(self)

    def process_command(self, user_input):
        """Processes a user command, determines intent, and executes actions."""
        # Log to memory
        self.memory.log_interaction("user", user_input)

        # 1. Clean and Sanitize Input
        cleaned_input = VedaSanitizer.clean_input(user_input)
        if not cleaned_input:
            return

        # 2. Tactical Fast-Path (Survival Mode)
        intent_data = self.planner.extract(cleaned_input)

        # 3. Fallback to LLM for complex intent extraction
        if not intent_data:
             intent_data = self.llm.extract_intent(cleaned_input)

        intent = intent_data.get("intent", "none")
        params = intent_data.get("params", {})

        response = ""
        action_taken = False

        # 4. Execute Feature based on Intent
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
            query = params.get("query", cleaned_input)
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
            note_text = params.get("text", cleaned_input)
            response = self.tools.take_note(note_text)
            action_taken = True
        elif intent == "find":
            query = params.get("query", cleaned_input)
            response = self.system.find(query)
            action_taken = True
        elif intent == "move":
            source = params.get("source", "")
            destination = params.get("destination", "")
            response = self.system.move(source, destination)
            action_taken = True
        elif intent == "add_task":
            task = params.get("task", cleaned_input)
            response = self.tasks.add_task(task)
            action_taken = True
        elif intent == "list_tasks":
            response = self.tasks.list_tasks()
            action_taken = True
        elif intent == "set_mode":
            mode = params.get("mode", cleaned_input)
            response = self.modes.set_mode(mode)
            action_taken = True

        # 5. If no specific action or we want a conversational response
        if not action_taken or "none" in intent:
            response = self.llm.chat(cleaned_input)

        # Log assistant response
        self.memory.log_interaction("assistant", response)

        # 6. Update UI and Speak
        self.gui.update_chat("Veda", response)
        self.voice.speak(response)

    def listen_and_process(self):
        """Listens for voice input and processes it."""
        query = self.voice.listen()
        if query != "None":
            self.gui.update_chat("You", query)
            self.process_command(query)
        self.gui.reset_voice_button()
