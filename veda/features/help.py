class VedaHelp:
    @staticmethod
    def get_command_list():
        """Returns a structured list of all Veda commands."""
        commands = {
            "System Control": [
                "Open [App Name] (e.g., 'Open Chrome')",
                "Close [App Name]",
                "Set Volume [0-100]",
                "Set Brightness [0-100]",
                "Lock PC",
                "Take a Screenshot",
                "System Health (CPU/RAM status)",
                "Network Info / Storage Info"
            ],
            "Media & Entertainment": [
                "Play [Song Name] (Direct YouTube playback)",
                "Pause music / Play music / Stop music",
                "Next track / Previous track",
                "Translate [Text] to [Language]"
            ],
            "Intelligence & Research": [
                "Search for [Topic] (Web Search)",
                "Deep research on [Topic] (Wikipedia)",
                "Summarize URL [Link]",
                "Read document [Path to PDF/Text]",
                "Calculate [Expression] (e.g., '2 + 2' or 'sqrt(16)')",
                "Remember that [Key] is [Value]"
            ],
            "Productivity": [
                "Take a note: [Content]",
                "Add to todo: [Task]",
                "Show my todo list",
                "Complete task [Number]",
                "Start Pomodoro [Minutes]",
                "Find file [Name]"
            ],
            "Vision & Sensors": [
                "What am I looking at? (Active window analysis)",
                "Look through the camera (Webcam vision)"
            ],
            "Modes & Protocols": [
                "Focus Mode / Stealth Mode / Gaming Mode / Normal Mode",
                "Run protocol [Name] (e.g., 'Run protocol House Party')",
                "Start recording macro / Stop recording macro",
                "Play macro [Name]"
            ],
            "Life & Wellness": [
                "What is the weather in [City]?",
                "Give me some motivation",
                "Check [Stock/Crypto] price (e.g., 'Check Bitcoin price')"
            ]
        }

        output = "AVAILABLE VEDA COMMANDS:\n\n"
        for category, cmds in commands.items():
            output += f"--- {category.upper()} ---\n"
            for cmd in cmds:
                output += f"• {cmd}\n"
            output += "\n"

        return output
