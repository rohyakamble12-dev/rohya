try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
import threading
import time

class SchedulerPlugin:
    def __init__(self, assistant):
        self.assistant = assistant
        self.running = True
        if SCHEDULE_AVAILABLE:
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()

    def register_intents(self):
        return {
            "schedule_task": self.schedule_command
        }

    def _run_scheduler(self):
        while self.running:
            try:
                schedule.run_pending()
            except: pass
            time.sleep(10)

    def schedule_command(self, params):
        if not SCHEDULE_AVAILABLE:
            return "Scheduler offline: schedule library not installed."
        command = params.get("command")
        minutes = int(params.get("delay", 1))

        schedule.every(minutes).minutes.do(self.assistant.process_command, command).tag('once')
        return f"Task scheduled: '{command}' in {minutes} minutes."
