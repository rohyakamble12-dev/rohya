import psutil
import time
import threading

class MonitorModule:
    def __init__(self, assistant):
        self.assistant = assistant
        self.running = True
        self.thresholds = {"cpu": 90, "ram": 90, "battery": 20}

    def start(self):
        threading.Thread(target=self._watch_loop, daemon=True).start()

    def _watch_loop(self):
        while self.running:
            try:
                # 1. CPU
                cpu = psutil.cpu_percent()
                if cpu > self.thresholds["cpu"]:
                    self.assistant.notify(f"TACTICAL ALERT: CPU Load at {cpu}%.")

                # 2. RAM
                ram = psutil.virtual_memory().percent
                if ram > self.thresholds["ram"]:
                    self.assistant.notify(f"TACTICAL ALERT: Memory usage critical at {ram}%.")

                # 3. Battery
                battery = psutil.sensors_battery()
                if battery and not battery.power_plugged and battery.percent < self.thresholds["battery"]:
                    self.assistant.notify(f"POWER ALERT: Reserve power at {battery.percent}%.")

            except: pass
            time.sleep(60) # Watch every minute

    def stop(self):
        self.running = False
