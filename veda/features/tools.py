import datetime
import os

class VedaTools:
    @staticmethod
    def take_note(text):
        """Saves a note to a local file."""
        try:
            filename = "veda_notes.txt"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(filename, "a") as f:
                f.write(f"[{timestamp}] {text}\n")
            return "I've saved that note for you."
        except Exception as e:
            return f"Failed to save note: {str(e)}"

    @staticmethod
    def get_time():
        """Returns the current time."""
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}"

    @staticmethod
    def get_date():
        """Returns today's date."""
        today = datetime.datetime.now().strftime("%B %d, %Y")
        return f"Today is {today}"

    @staticmethod
    def start_pomodoro(minutes):
        """Starts a basic pomodoro timer in a background thread."""
        try:
            minutes = int(minutes)

            def timer_thread():
                import time
                try:
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                except ImportError:
                    toaster = None

                time.sleep(minutes * 60)

                # Notify completion
                if toaster:
                    toaster.show_toast("Veda Pomodoro", f"Your {minutes} minute focus session is complete.", duration=10, threaded=True)

                # Optional fallback audible alert or logging
                filename = "veda_notes.txt"
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    with open(filename, "a") as f:
                        f.write(f"[{timestamp}] Pomodoro timer of {minutes} minutes finished.\n")
                except:
                    pass

            import threading
            t = threading.Thread(target=timer_thread, daemon=True)
            t.start()
            return f"Pomodoro timer started for {minutes} minutes. Focus up."
        except Exception as e:
            return f"Failed to start pomodoro timer: {str(e)}"
