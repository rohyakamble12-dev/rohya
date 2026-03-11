import schedule
import threading
import time

class SchedulerPlugin:
    def __init__(self, assistant):
        self.assistant = assistant
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()

    def register_intents(self):
        return {
            "schedule_task": self.schedule_command
        }

    def _run_scheduler(self):
        while self.running:
            schedule.run_pending()
            time.sleep(10)

    def schedule_command(self, params):
        command = params.get("command")
        minutes = int(params.get("delay", 1))

        schedule.every(minutes).minutes.do(self.assistant.process_command, command).tag('once')
        return f"Task scheduled: '{command}' in {minutes} minutes."
