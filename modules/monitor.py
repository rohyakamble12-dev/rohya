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
        last_net_state = True
        last_window = ""
        last_ocr_time = 0
        while self.running:
            try:
                # 1. Resource Consumption
                cpu = psutil.cpu_percent()
                if cpu > self.thresholds["cpu"]:
                    self.assistant.notify(f"TACTICAL ALERT: CPU Load at {cpu}%. Optimize active processes.")

                ram = psutil.virtual_memory().percent
                if ram > self.thresholds["ram"]:
                    self.assistant.notify(f"TACTICAL ALERT: Memory usage critical at {ram}%.")

                # 2. Power State
                battery = psutil.sensors_battery()
                if battery and not battery.power_plugged and battery.percent < self.thresholds["battery"]:
                    self.assistant.notify(f"POWER ALERT: Reserve power at {battery.percent}%. Connect to power source.")

                # 3. Network Link (Proactive)
                import socket
                try:
                    socket.create_connection(("1.1.1.1", 53), timeout=2)
                    current_net = True
                except: current_net = False

                if current_net != last_net_state:
                    self.assistant.notify(f"NETWORK ALERT: Data link {'established' if current_net else 'lost'}. Synchronizing interface.")
                    last_net_state = current_net

                # 4. Active Window (Proactive Workflow)
                current_win = self.assistant.router.system.get_active_window()
                if "Focus:" in current_win and current_win != last_window:
                    if "code" in current_win.lower() or "studio" in current_win.lower():
                        self.assistant.notify("Workflow detected: Development sector active. Stand by for tactical support.")
                    last_window = current_win

                # 5. Autonomous OCR (Sentinel Mode)
                if time.time() - last_ocr_time > 300: # Every 5 mins
                    ocr_res = self.assistant.router.vision.screen_ocr()
                    if "INTEGRITY" in ocr_res:
                        self.assistant.memory.save_state("screen_context", ocr_res)
                    last_ocr_time = time.time()

            except: pass
            time.sleep(45) # Watch every 45s

    def stop(self):
        self.running = False
