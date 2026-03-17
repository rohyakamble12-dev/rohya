import time
import threading, time

class ProductivityModule:
    def __init__(self, assistant):
        self.assistant = assistant

    def start_pomodoro(self, minutes=25):
        def _run():
            time.sleep(minutes * 60)
            self.assistant.notify("Pomodoro Complete.")
        threading.Thread(target=_run, daemon=True).start()
        return f"Pomodoro started: {minutes}m."

    def remind_me(self, task, minutes):
        def _remind():
            time.sleep(minutes * 60)
            self.assistant.notify(f"REMINDER: {task}")
        threading.Thread(target=_remind, daemon=True).start()
        return f"Reminder set for {task} in {minutes}m."
