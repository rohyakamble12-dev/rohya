class VedaContext:
    def __init__(self):
        self.version = "4.1.0"
        self.codename = "Ultimate HUD Edition"
        self.creator = "Marvel Legacy"
        self.online_voice = "en-US-AvaNeural"
        self.primary_model = "qwen2.5:3b"
        self.fallback_model = "tinyllama"

        # UI Themes
        self.themes = {
            "stark": "#00d4ff",   # Cyan
            "stealth": "#707070", # Gray
            "hazard": "#ff4b2b",  # Red
            "focus": "#00ff7f"    # Green
        }
        self.current_theme = "stark"

        # Tactical Thresholds
        self.confidence_threshold = 0.8
        self.timeout_neural = 10
        self.timeout_survival = 5

        # Resource Paths
        self.storage_root = "veda/storage/"
        self.memory_db = "veda/storage/veda_memory.db"
        self.notes_file = "veda/storage/notes.txt"
        self.calendar_db = "veda/storage/calendar.db"
        self.macro_file = "veda/storage/macros.json"

    def get_summary(self):
        return f"VEDA {self.version} | CODENAME: {self.codename}"

    def get_accent(self):
        return self.themes.get(self.current_theme, "#00d4ff")
