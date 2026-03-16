from veda.core.llm import VedaLLM
from veda.core.voice import VedaVoice
from veda.core.planner import TacticalFastPath
from veda.core.memory import VedaMemory
from veda.core.plugin_manager import PluginManager
from veda.core.context import VedaContext
from veda.utils.sanitizer import VedaSanitizer

class VedaAssistant:
    def __init__(self, gui):
        self.ctx = VedaContext()
        self.gui = gui
        self.memory = VedaMemory(self.ctx.memory_db)
        self.llm = VedaLLM(self.ctx.primary_model)
        self.voice = VedaVoice(self.ctx.online_voice)
        self.planner = TacticalFastPath()

        # Initialize Plugin System
        self.plugin_manager = PluginManager(self)
        self.plugin_manager.discover_and_load()

    def get_protocols(self):
        """Public getter for protocol states."""
        return self.gui.state.protocols

    def process_command(self, user_input):
        """Processes a user command via the tiered pipeline."""
        if user_input == "system_stats_internal":
            return self.plugin_manager.handle_intent("system_stats", {})

        if user_input == "check_neural_link":
            return self.llm.check_link()

        self.memory.log_interaction("user", user_input)
        cleaned_input = VedaSanitizer.clean_input(user_input)
        if not cleaned_input:
            return

        # Update UI to thinking state
        self.gui.set_state("thinking")

        # 1. Update Execution Plan Visualizer
        self.gui.left.update_plan(f"Resolving intent: {cleaned_input[:20]}...")

        # 2. Tactical Fast-Path (Survival Mode)
        intent_data = self.planner.extract(cleaned_input)

        # 3. Fallback to LLM Intent
        if not intent_data:
             intent_data = self.llm.extract_intent(cleaned_input)

        intent = intent_data.get("intent", "none")
        params = intent_data.get("params", {})
        self.gui.left.update_plan(f"Intent extracted: {intent}")

        # 4. Handle via Tactical Modules (Plugins)
        # Check for profile shift first
        if intent == "set_mode":
            mode = params.get("mode", "").lower()
            if mode in self.ctx.themes:
                self.ctx.current_theme = mode
                self.gui.set_theme_color(self.ctx.get_accent())
                response = f"UI profile synchronized to {mode.upper()}."
            else:
                response = self.plugin_manager.handle_intent(intent, params)
        else:
            response = self.plugin_manager.handle_intent(intent, params)

        # 5. Final Fallback to Neural Link (Chat)
        if response is None:
            response = self.llm.chat(cleaned_input)

        # 6. UI Vocalization & State Cycle
        self.gui.set_state("speaking")
        self.memory.log_interaction("assistant", response)
        self.gui.update_chat("Veda", response)
        self.voice.speak(response)
        self.gui.set_state("idle")
        self.gui.left.update_plan("Standby.")

    def listen_and_process(self):
        """Listens for voice input and processes it."""
        query = self.voice.listen()
        if query != "None":
            self.gui.update_chat("You", query)
            self.process_command(query)
        self.gui.reset_voice_button()
