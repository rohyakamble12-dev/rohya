import logging

# Set up logging for resilient modules
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VEDA")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    logger.warning("[SYSTEM]: psutil missing. Hardware diagnostics disabled.")
    PSUTIL_AVAILABLE = False

class SystemMonitor:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "system_stats": self.get_stats,
            "battery_info": self.get_battery
        }

    def get_stats(self, params=None):
        if not PSUTIL_AVAILABLE:
            return "Hardware monitoring module (psutil) is currently offline."
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory().percent
            return f"CPU Load: {cpu}%\nRAM Load: {ram}%"
        except Exception as e:
            return f"Diagnostic failure: {e}"

    def get_battery(self, params=None):
        if not PSUTIL_AVAILABLE:
            return "Power monitoring module is currently offline."
        try:
            battery = psutil.sensors_battery()
            if battery:
                status = "Charging" if battery.power_plugged else "Discharging"
                return f"Battery Level: {battery.percent}% ({status})"
            return "Power statistics unavailable for this hardware."
        except Exception as e:
            return f"Power diagnostic failure: {e}"
