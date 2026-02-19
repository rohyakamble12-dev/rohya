import time
import threading

class VedaTaskMaster:
    def __init__(self, assistant_ref):
        self.assistant = assistant_ref
        self.todo_list = []
        self.pomodoro_active = False

    def add_todo(self, task):
        self.todo_list.append({"task": task, "completed": False})
        return f"Added '{task}' to your todo list."

    def get_todos(self):
        if not self.todo_list:
            return "Your todo list is empty."

        status = "Current Tasks:\n"
        for i, item in enumerate(self.todo_list):
            mark = "[X]" if item["completed"] else "[ ]"
            status += f"{i+1}. {mark} {item['task']}\n"
        return status

    def complete_todo(self, index):
        try:
            self.todo_list[index-1]["completed"] = True
            return f"Task {index} marked as completed."
        except:
            return "Invalid task number."

    def start_pomodoro(self, minutes=25):
        if self.pomodoro_active:
            return "A Pomodoro timer is already running."

        self.pomodoro_active = True
        threading.Thread(target=self._run_pomodoro, args=(minutes,), daemon=True).start()
        return f"Pomodoro timer started for {minutes} minutes. Focus time!"

    def _run_pomodoro(self, minutes):
        time.sleep(minutes * 60)
        self.pomodoro_active = False
        self.assistant.system_alert("Pomodoro complete! Take a well-deserved break.")
