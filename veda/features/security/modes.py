import psutil
from veda.features.base import VedaPlugin, PermissionTier

class ModePlugin(VedaPlugin):
    def setup(self):
        self.active_mode = "NORMAL"

        self.register_intent("focus_mode", self.focus_mode, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("stealth_mode", self.stealth_mode, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("gaming_mode", self.gaming_mode, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("normal_mode", self.normal_mode, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("clean_slate", self.clean_slate, PermissionTier.CONFIRM_REQUIRED,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("house_party", self.house_party_protocol, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("describe_modes", self.describe_modes, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("set_mode", self.set_mode, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"mode": {"type": "string"}}, "required": ["mode"], "additionalProperties": False})

    def get_mode_data(self):
        return {
            "NORMAL": "Standard operating state. Restores 50% volume, 70% brightness, and standard UI opacity. Context monitoring is active.",
            "FOCUS": "Optimized for deep work. Sets 20% volume, 40% brightness, yellow UI theme, and enables context monitoring.",
            "STEALTH": "Minimal presence. Mutes system volume, sets 40% UI transparency, grey UI theme, and disables monitoring.",
            "GAMING": "Performance optimized. Maximizes brightness, sets 30% UI transparency, and identifies high-memory tasks.",
            "CLEAN_SLATE": "Reduces entropy. Automatically identifies and closes non-essential windows to clear your workspace.",
            "HOUSE_PARTY": "Social protocol. Increases volume to 80%, sets green success theme, plays upbeat music, and opens web apps."
        }

    def describe_modes(self, params):
        """Returns a detailed list of all tactical modes and their capabilities."""
        descriptions = self.get_mode_data()
        msg = "Sir, I have the following tactical modes available:\n\n"
        for mode, desc in descriptions.items():
            msg += f"● {mode}: {desc}\n"
        msg += "\nYou can ask me to 'engage [mode name]' at any time."
        return msg

    def set_mode(self, params):
        """Generic entry point for mode switching."""
        mode_req = params.get("mode", "").upper()

        mode_map = {
            "NORMAL": self.normal_mode,
            "FOCUS": self.focus_mode,
            "STEALTH": self.stealth_mode,
            "GAMING": self.gaming_mode,
            "CLEAN_SLATE": self.clean_slate,
            "HOUSE_PARTY": self.house_party_protocol
        }

        # Try exact match first
        if mode_req in mode_map:
             return mode_map[mode_req]({})

        # Fuzzy matching for better UX
        for key in mode_map:
            if key in mode_req or (len(mode_req) > 3 and mode_req in key):
                return mode_map[key]({})

        return f"Sir, the requested mode '{mode_req}' is not in my tactical database. Try 'describe modes' for a full list."

    def focus_mode(self, params):
        """Optimizes system for focus."""
        self.active_mode = "FOCUS"
        # 1. Set volume to a lower, focus-friendly level
        self.assistant.process_command("set volume 20", is_subcommand=True)
        # 2. Lower brightness for eye comfort
        self.assistant.process_command("set brightness 40", is_subcommand=True)
        # 3. Update Theme via GUI
        self.assistant.gui.after(0, lambda: self.assistant.gui.set_theme_color("focus"))
        # 4. Protocol updates
        self.assistant.protocols.protocols["context_monitoring"] = True
        return "Focus Mode Engaged. I've optimized your environment for deep work, Sir."

    def stealth_mode(self, params):
        """Minimizes Veda's presence."""
        self.active_mode = "STEALTH"
        self.assistant.process_command("set volume 0", is_subcommand=True)
        self.assistant.gui.after(0, lambda: self.assistant.gui.attributes("-alpha", 0.4))
        self.assistant.gui.after(0, lambda: self.assistant.gui.set_theme_color("stealth"))
        self.assistant.protocols.protocols["context_monitoring"] = False
        self.assistant.context.stop_monitoring()
        return "Stealth Mode Active. I will remain in the shadows, Sir."

    def gaming_mode(self, params):
        """Optimizes system for high performance gaming."""
        self.active_mode = "GAMING"
        self.assistant.process_command("set brightness 100", is_subcommand=True)
        self.assistant.gui.after(0, lambda: self.assistant.gui.attributes("-alpha", 0.3))

        count = 0
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                if proc.info['memory_info'].rss > 500 * 1024 * 1024:
                    count += 1
            except Exception: pass

        return f"Gaming Mode engaged. System levels optimized. Found {count} high-memory background tasks, Sir."

    def normal_mode(self, params):
        """Restores standard settings."""
        self.active_mode = "NORMAL"
        self.assistant.process_command("set volume 50", is_subcommand=True)
        self.assistant.process_command("set brightness 70", is_subcommand=True)
        self.assistant.gui.after(0, lambda: self.assistant.gui.attributes("-alpha", 0.95))
        self.assistant.gui.after(0, lambda: self.assistant.gui.set_theme_color("calm"))
        self.assistant.protocols.protocols["context_monitoring"] = True
        self.assistant.context.start_monitoring()
        return "Standard protocols restored, Sir."

    def house_party_protocol(self, params):
        """Initiates House Party Protocol: Setting the mood."""
        self.active_mode = "HOUSE_PARTY"
        self.assistant.gui.after(0, lambda: self.assistant.gui.set_theme_color("success"))

        # 1. Play some upbeat music (or search for it)
        self.assistant.process_command("play upbeat party music", is_subcommand=True)
        # 2. Increase volume
        self.assistant.process_command("set volume 80", is_subcommand=True)
        # 3. Open fun apps
        self.assistant.process_command("open chrome", is_subcommand=True)

        return "House Party Protocol initiated. Mood levels optimized, Sir."

    def clean_slate(self, params):
        """Reduces system entropy by closing non-essential windows."""
        try:
            import pygetwindow as gw
        except (ImportError, NotImplementedError):
            return "Sovereign Block: Window control restricted on this platform."

        self.active_mode = "CLEAN_SLATE"

        # 1. Visual Feedback
        self.assistant.gui.after(0, lambda: self.assistant.gui.set_theme_color("alert"))

        # 2. Strategic Window Purge
        all_windows = gw.getAllWindows()
        closed_count = 0
        whitelist = ["VEDA CORE", "Program Manager", "Settings", "Task Manager", "Calculator"]

        for window in all_windows:
            if window.title and window.title not in whitelist:
                try:
                    window.close()
                    closed_count += 1
                except Exception: pass

        # 3. Restore Calm
        self.assistant.gui.after(3000, lambda: self.assistant.gui.set_theme_color("calm"))
        return f"Clean Slate Protocol complete. Purged {closed_count} non-essential sectors, Sir."
