import time
import threading

class VedaLife:
    def __init__(self, assistant_ref):
        self.assistant = assistant_ref
        self.reminders_active = True
        self.last_water_break = time.time()
        self.last_eye_break = time.time()

    def start_routine_monitor(self):
        """Starts a background thread to monitor health routines."""
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def _monitor_loop(self):
        while self.reminders_active:
            current_time = time.time()

            # Water break every 1 hour
            if current_time - self.last_water_break > 3600:
                self.assistant.system_alert("Time for a hydration break. Stay sharp.")
                self.last_water_break = current_time

            # Eye break every 20 mins
            if current_time - self.last_eye_break > 1200:
                self.assistant.system_alert("20 minutes passed. Look 20 feet away for 20 seconds.")
                self.last_eye_break = current_time

            time.sleep(60) # Check every minute

    @staticmethod
    def get_motivation():
        """Returns a random motivational quote."""
        quotes = [
            "The only way to do great work is to love what you do.",
            "Efficiency is doing things right; effectiveness is doing the right things.",
            "The best way to predict the future is to create it.",
            "I have not failed. I've just found 10,000 ways that won't work."
        ]
        import random
        return random.choice(quotes)
