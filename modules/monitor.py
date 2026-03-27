import psutil
import time
import threading
import socket

class MonitorModule:
    def __init__(self, assistant):
        self.assistant = assistant
        self.running = True
        self.thresholds = {"cpu": 90, "ram": 90, "battery": 20, "disk": 90}

    def start(self):
        threading.Thread(target=self._watch_loop, daemon=True).start()

    def _watch_loop(self):
        last_net_state = True
        last_window = ""
        last_ocr_time = 0
        last_ssid = ""
        while self.running:
            try:
                # 1. Resource Consumption
                cpu = psutil.cpu_percent()
                if cpu > self.thresholds["cpu"]:
                    self.assistant.notify(f"TACTICAL ALERT: CPU Load at {cpu}%. Optimize active processes.")

                ram = psutil.virtual_memory().percent
                if ram > self.thresholds["ram"]:
                    self.assistant.notify(f"TACTICAL ALERT: Memory usage critical at {ram}%.")

                disk = psutil.disk_usage('/').percent
                if disk > self.thresholds["disk"]:
                    self.assistant.notify(f"TACTICAL ALERT: Primary drive capacity at {disk}%. Initiate cleanup protocol.")

                # 2. Power State
                battery = psutil.sensors_battery()
                if battery and not battery.power_plugged and battery.percent < self.thresholds["battery"]:
                    self.assistant.notify(f"POWER ALERT: Reserve power at {battery.percent}%. Connect to power source.")

                # 3. Network Link (SSID Detection)
                try:
                    socket.create_connection(("1.1.1.1", 53), timeout=2)
                    current_net = True
                except: current_net = False

                net_info = self.assistant.router.system.get_network_info()
                current_ssid = net_info.split("SSID:")[1].strip() if "SSID:" in net_info else "Unknown"

                if current_net != last_net_state:
                    self.assistant.notify(f"NETWORK ALERT: Data link {'established' if current_net else 'lost'}. SSID: {current_ssid}.")
                    last_net_state = current_net
                elif current_ssid != last_ssid and current_net:
                    self.assistant.notify(f"NETWORK UPDATE: Roaming detected. Connected to '{current_ssid}'.")
                last_ssid = current_ssid

                # 4. Active Window (Proactive Workflow)
                current_win = self.assistant.router.system.get_active_window()
                if "Focus:" in current_win and current_win != last_window:
                    if "code" in current_win.lower() or "studio" in current_win.lower():
                        self.assistant.notify("Workflow detected: Development sector active. Prepared for tactical support.")
                    elif "chrome" in current_win.lower() or "edge" in current_win.lower():
                        self.assistant.notify("Intelligence gathering detected. Search protocols online.")
                    last_window = current_win

                # 5. Autonomous OCR (Sentinel Mode)
                if time.time() - last_ocr_time > 300: # Every 5 mins
                    ocr_res = self.assistant.router.vision.screen_ocr()
                    if "INTEGRITY" in ocr_res:
                        self.assistant.memory.save_state("screen_context", ocr_res)
                    last_ocr_time = time.time()

            except: pass
            time.sleep(30) # High-fidelity watch every 30s

    def stop(self):
        self.running = False
