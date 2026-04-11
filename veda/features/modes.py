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
        elif mode_name == "clean slate":
             return self.clean_slate_protocol()
        elif mode_name == "mark 42":
             return self.mark_42_status()
        elif mode_name == "gaming":
             return self.gaming_mode()
        else:
            self.active_mode = "standard"
            return "Switched to standard mode."

    def house_party_protocol(self):
        """Automates multiple actions for a party."""
        self.assistant.system.set_volume(80)
        # Launch a YouTube playlist
        import webbrowser
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLx0sYbCqOb8TBPRdmBHs5Iftvv9CB5HCq")
        return "House Party Protocol engaged. Volume optimized. Launching entertainment."

    def clean_slate_protocol(self):
        """Instant shutdown of non-essential work apps and system muting."""
        return self.assistant.system.clean_slate()

    def mark_42_status(self):
        """Full diagnostic report."""
        return self.assistant.system.system_health()

    def focus_mode(self):
        """Silences distractions."""
        self.assistant.system.set_volume(0)
        return "Focus mode enabled. Distractions minimized."

    def gaming_mode(self):
        """Optimizes for gaming."""
        self.assistant.system.set_volume(70)
        return "Gaming mode enabled. Ready to play."

    def get_modes(self):
        return ["standard", "house party", "focus", "clean slate", "mark 42", "gaming"]
