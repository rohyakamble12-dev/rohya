import psutil

class SystemMonitor:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "system_stats": self.get_stats,
            "battery_info": self.get_battery
        }

    def get_stats(self, params=None):
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        return f"CPU Usage: {cpu}%\nRAM Usage: {ram}%"

    def get_battery(self, params=None):
        battery = psutil.sensors_battery()
        if battery:
            status = "Plugged in" if battery.power_plugged else "Discharging"
            return f"Battery: {battery.percent}% ({status})"
        return "Battery info unavailable."
