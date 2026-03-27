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
            # First perform hot-reload
            reload_res = self.assistant.hot_reload()
            # Then run diagnostic
            subprocess.Popen(["python", "check_startup.py"], creationflags=0x08000000)
            return f"ULTRON PROTOCOL: {reload_res} Initiating self-diagnostic sequences."
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

    def barn_door(self):
        """MCU Accurate Barn Door Protocol: Total System Isolation."""
        self.assistant.process_command("close all")
        self.assistant.process_command("set clipboard clear")
        self.assistant.process_command("set dnd true")
        self.assistant.process_command("optimize_system")
        self.assistant.process_command("lock pc")
        return "BARN DOOR PROTOCOL: Total system isolation engaged. Critical data sectors sealed and purged."

    def legionnaire(self):
        """MCU Accurate Legionnaire Protocol: Sentinel Overdrive."""
        self.assistant.monitor.thresholds = {"cpu": 60, "ram": 60, "battery": 30} # Tighter thresholds
        self.assistant.process_command("network_discovery")
        return "LEGIONNAIRE PROTOCOL: Sentinel sensitivity at maximum. Tactical monitoring overlapping all sectors."

    def verity(self, claim):
        """MCU Accurate Verity Protocol: Truth/Fact verification."""
        if not claim: return "VERITY PROTOCOL: No claim provided for analysis."
        res = self.assistant.router.intel.deep_research(f"Fact check: {claim}")
        return f"VERITY ANALYSIS: {claim}\nREPORT: {res}\nConfidence level: ANALYZED."
