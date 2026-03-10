class ModeManager:
    def __init__(self, assistant):
        self.assistant = assistant
        self.active_mode = "standard"

    def set_mode(self, mode_name):
        mode_name = mode_name.lower()
        if mode_name == "house party":
            return self.house_party_protocol()
        elif mode_name == "focus":
             return self.focus_mode()
        else:
            self.active_mode = "standard"
            return "Switched to standard mode."

    def house_party_protocol(self):
        """Automates multiple actions for a party."""
        self.assistant.system.set_volume(80)
        self.assistant.system.open_app("chrome")
        return "House Party Protocol engaged. Volume optimized. Launching entertainment."

    def focus_mode(self):
        """Silences distractions."""
        self.assistant.system.set_volume(0)
        return "Focus mode enabled. Distractions minimized."

    def get_modes(self):
        return ["standard", "house party", "focus"]
