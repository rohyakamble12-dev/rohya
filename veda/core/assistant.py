from veda.core.llm import VedaLLM
from veda.core.voice import VedaVoice
from veda.features.system_control import SystemControl
from veda.features.web_info import WebInfo
from veda.features.tools import VedaTools

class VedaAssistant:
    def __init__(self, gui):
        self.gui = gui
        self.llm = VedaLLM()
        self.voice = VedaVoice()
        self.system = SystemControl()
        self.web = WebInfo()
        self.tools = VedaTools()

    def process_command(self, user_input):
        """Processes a user command, determines intent, and executes actions."""
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

        # 3. If no specific action or we want a conversational response
        if not action_taken or "none" in intent:
            response = self.llm.chat(user_input)

        # 4. Update UI and Speak
        self.gui.update_chat("Veda", response)
        self.voice.speak(response)

    def listen_and_process(self):
        """Listens for voice input and processes it."""
        query = self.voice.listen()
        if query != "None":
            self.gui.update_chat("You", query)
            self.process_command(query)
        self.gui.reset_voice_button()
