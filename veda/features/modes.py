class ModeManager:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "set_mode": self.set_mode
        }

    def set_mode(self, params):
        mode_name = params.get("mode", "").lower()
        if "house party" in mode_name:
            self.assistant.plugin_manager.handle_intent("set_volume", {"level": 80})
            self.assistant.plugin_manager.handle_intent("open_app", {"app_name": "chrome"})
            self.assistant.gui.update_protocol("House Party")
            return "House Party Protocol engaged. Entertainment systems active."
        elif "focus" in mode_name:
            self.assistant.plugin_manager.handle_intent("set_volume", {"level": 0})
            self.assistant.gui.update_protocol("Focus")
            return "Focus mode active. Distractions eliminated."
        else:
            self.assistant.gui.update_protocol("Standard")
            return "Interface reset to standard mode."
