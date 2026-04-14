import time
from veda.features.base import VedaPlugin, PermissionTier
from veda.utils.threads import manager as thread_manager

class LifePlugin(VedaPlugin):
    def setup(self):
        self.reminders_active = True
        self.last_water_break = time.time()
        self.last_eye_break = time.time()

        self.register_intent("set_timer", self.set_timer, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"minutes": {"type": "integer"}, "label": {"type": "string"}}, "required": ["minutes"], "additionalProperties": False})
        self.register_intent("set_alarm", self.set_alarm, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"time": {"type": "string"}, "label": {"type": "string"}}, "required": ["time"], "additionalProperties": False})
        self.register_intent("motivation", self.get_motivation, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})

        thread_manager.run_with_throttle("HealthMonitor", self._monitor_step, interval=60.0)

    def set_timer(self, params):
        minutes = params.get("minutes", 5)
        label = params.get("label", "General Timer")
        try:
            seconds = int(minutes) * 60
        except ValueError:
            return "Error: Minutes must be an integer."

        # Uniquify thread name to allow multiple timers
        t_name = f"Timer_{label}_{int(time.time())}"
        thread_manager.start_thread(t_name, self._timer_worker, args=(seconds, label))
        return f"Timer established for {minutes} minutes."

    def _timer_worker(self, seconds, label):
        time.sleep(seconds)
        self.assistant.system_alert(f"TIMER COMPLETE: {label}")

    def set_alarm(self, params):
        time_str = params.get("time", "08:00")
        label = params.get("label", "Alarm")
        t_name = f"Alarm_{label}_{time_str}_{int(time.time())}"
        thread_manager.start_thread(t_name, self._alarm_worker, args=(time_str, label))
        return f"Alarm established for {time_str}."

    def _alarm_worker(self, time_str, label):
        from datetime import datetime
        while self.reminders_active:
            now = datetime.now().strftime("%H:%M")
            if now == time_str:
                self.assistant.system_alert(f"ALARM TRIGGERED: {label}")
                break
            time.sleep(30)

    def _monitor_step(self):
        current_time = time.time()
        if current_time - self.last_water_break > 3600:
            self.assistant.system_alert("Hydration break recommended.")
            self.last_water_break = current_time
        if current_time - self.last_eye_break > 1200:
            self.assistant.system_alert("Eye rest protocol: 20-20-20 rule.")
            self.last_eye_break = current_time

    def get_motivation(self, params):
        import random
        return random.choice(["Stay focused.", "Excellence is a habit."])
