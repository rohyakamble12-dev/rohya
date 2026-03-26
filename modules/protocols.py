class ProtocolModule:
    def __init__(self, assistant):
        self.assistant = assistant

    def house_party(self):
        self.assistant.process_command("open chrome https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assistant.process_command("open calc")
        return "House Party Protocol engaged. Multi-system initialization complete."

    def clean_slate(self):
        self.assistant.process_command("close all") # Hypothetical broad close
        return "CLEAN SLATE PROTOCOL: All non-essential interfaces purged from active sectors."

    def mark_42(self):
        health = self.assistant.router.system.get_health()
        return f"MARK 42 STATUS: All systems green. {health}"

    def edith(self):
        """Even Dead, I'm The Hero - Security & Network Sentinel."""
        net = self.assistant.router.system.discover_network_devices()
        health = self.assistant.router.system.get_health()
        return f"E.D.I.T.H. ONLINE: Scanning local tactical environment...\n{net}\n{health}\nSecurity perimeter: ACTIVE."

    def ultron(self):
        """Self-Repair & Diagnostic Protocol."""
        import subprocess
        try:
            # Simulated repair by running the dependency check script
            subprocess.Popen(["python", "check_startup.py"], creationflags=0x08000000)
            return "ULTRON PROTOCOL: Initiating self-diagnostic and repair sequences. Re-indexing system links."
        except: return "ULTRON: Diagnostic link failed."

    def good_morning(self):
        """Morning Briefing: Weather, News, and Todos."""
        weather = self.assistant.router.intel.get_weather("current location")
        news = self.assistant.router.intel.get_news("top stories")
        todos = self.assistant.memory.get_todos()
        todo_str = f"You have {len(todos)} pending tasks." if todos else "No immediate tasks on your schedule."
        return f"GOOD MORNING. Systems initialization complete.\nENVIRONMENT: {weather}\nINTELLIGENCE: {news}\nPRODUCTIVITY: {todo_str}\nHave a productive day."

    def good_night(self):
        """Evening Routine: Sleep protocol."""
        self.assistant.process_command("set volume 0")
        self.assistant.process_command("lock pc")
        return "GOOD NIGHT. Sleep protocol engaged. Perimeter monitoring active. Rest well."

    def im_home(self):
        """Welcome Home: Music and Unlocking."""
        self.assistant.process_command("play music chill iron man mix")
        self.assistant.process_command("set brightness 80")
        return "WELCOME HOME. Establishing habitat synchronization. Ambient environment optimized."

    def security_lockdown(self):
        """Security Protocol: Stealth and Locking."""
        self.assistant.process_command("lock pc")
        self.assistant.process_command("vision describe")
        return "SECURITY LOCKDOWN: Peripheral interfaces severed. Perimeter scan initiated. System secured."
