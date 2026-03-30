import time
import threading
try:
    import schedule
    HAS_SCHEDULE = True
except ImportError:
    HAS_SCHEDULE = False

class ProductivityModule:
    def __init__(self, assistant):
        self.assistant = assistant
        self.running = True
        threading.Thread(target=self._scheduler_loop, daemon=True).start()

    def _scheduler_loop(self):
        if not HAS_SCHEDULE: return
        # Daily Briefing at 08:00
        schedule.every().day.at("08:00").do(self.daily_strategic_outlook)
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def daily_strategic_outlook(self):
        """Aggregated Daily Briefing."""
        res = self.assistant.router.protocols.good_morning()
        self.assistant.notify(f"DAILY STRATEGIC OUTLOOK: {res}")
        return res

    def start_pomodoro(self, minutes=25):
        def _run():
            time.sleep(minutes * 60)
            self.assistant.notify("TACTICAL ALERT: Pomodoro cycle complete. Take a mandatory rest period.")
        threading.Thread(target=_run, daemon=True).start()
        return f"Pomodoro cycle initiated: {minutes}m."

    def remind_me(self, task, time_str):
        """Supports 'in 5 minutes' or 'at 17:00'."""
        try:
            if "in" in time_str:
                mins = int(time_str.split()[1])
                def _remind():
                    time.sleep(mins * 60)
                    self.assistant.notify(f"TACTICAL REMINDER: {task}")
                threading.Thread(target=_remind, daemon=True).start()
                return f"Reminder logged: {task} in {mins}m."
            else:
                if not HAS_SCHEDULE: return "Absolute scheduling offline."
                # Expects HH:MM format for 'at'
                schedule.every().day.at(time_str).do(self.assistant.notify, f"SCHEDULED TASK: {task}")
                return f"Absolute schedule set for {task} at {time_str}."
        except Exception as e:
            return f"Scheduling error: {e}"

    def list_schedule(self):
        if not HAS_SCHEDULE: return "Scheduler interface offline."
        jobs = schedule.get_jobs()
        if not jobs: return "Daily schedule is clear, Operator."
        return "\n".join([f"{j.next_run}" for j in jobs])
