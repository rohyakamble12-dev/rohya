import requests
import random

class IOTModule:
    def __init__(self, assistant):
        self.assistant = assistant
        self.webhooks = assistant.config.get("webhooks", {})

    def trigger(self, device):
        url = self.webhooks.get(device)
        if not url: return f"HABITAT: Device '{device}' not found in tactical registry."
        try:
            res = requests.post(url, timeout=5)
            return f"HABITAT SYNC: '{device}' interface engaged." if res.status_code == 200 else f"HABITAT: '{device}' relay failed."
        except Exception as e: return f"Habitat link failure: {e}"

    def get_habitat_report(self):
        """Simulated environmental telemetry for immersion."""
        temp = random.randint(20, 25)
        humidity = random.randint(40, 60)
        load = random.randint(100, 1500) # Watts
        return (
            f"--- HABITAT TELEMETRY ---\n"
            f"AMBIENT: {temp}°C | HUMIDITY: {humidity}%\n"
            f"ENERGY DRAW: {load}W (NOMINAL)\n"
            f"STATUS: Habitat synchronization active."
        )

    def set_scene(self, scene_name):
        """Orchestrates multiple IOT devices for specific environments."""
        scene_name = scene_name.lower()
        if "movie" in scene_name or "cinema" in scene_name:
            self.trigger("lights_main_off")
            self.trigger("led_strip_blue")
            return "SCENE ENGAGED: Cinematic environment initialized. Enjoy the screening, Operator."
        elif "work" in scene_name or "focus" in scene_name:
            self.trigger("lights_desk_on")
            self.trigger("led_strip_white")
            return "SCENE ENGAGED: Focus parameters initialized. Lighting optimized for productivity."
        return f"Scene '{scene_name}' not configured in habitat sectors."
