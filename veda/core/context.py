class VedaContext:
    def __init__(self):
        self.version = "3.2.0"
        self.codename = "Qwen Edition"
        self.creator = "Marvel Legacy"
        self.online_voice = "en-US-AvaNeural" # Edge TTS voice
        self.primary_model = "qwen2.5:3b"
        self.fallback_model = "tinyllama"

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
