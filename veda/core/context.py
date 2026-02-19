import pygetwindow as gw
import time
import threading

class VedaContext:
    def __init__(self, assistant_ref):
        self.assistant = assistant_ref
        self.active_app = None
        self.active_window_title = None
        self.is_monitoring = False

        # Privacy Blacklist: Apps that Veda should ignore for real-time context
        self.privacy_blacklist = [
            "password", "bitwarden", "keepass", "private", "incognito",
            "banking", "finance", "bank", "credit card", "login"
        ]

    def start_monitoring(self):
        """Starts the background context monitor."""
        if not self.is_monitoring:
            self.is_monitoring = True
            threading.Thread(target=self._monitor_loop, daemon=True).start()

    def stop_monitoring(self):
        self.is_monitoring = False

    def _is_sensitive(self, title):
        """Checks if the window title contains sensitive keywords."""
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in self.privacy_blacklist)

    def _monitor_loop(self):
        while self.is_monitoring:
            try:
                window = gw.getActiveWindow()
                if window and window.title:
                    title = window.title

                    # Security Check: Ignore sensitive windows
                    if self._is_sensitive(title):
                        if self.active_app != "PRIVATE":
                            self.active_app = "PRIVATE"
                            self.active_window_title = "Data Shield Active"
                            print("Context Monitor: Privacy Shield Engaged.")
                    else:
                        if title != self.active_window_title:
                            self.active_window_title = title
                            # Simple app extraction from title (usually end of string)
                            self.active_app = title.split(' - ')[-1] if ' - ' in title else title

                            # Proactively notify assistant if it's a significant change
                            self.assistant.on_context_change(self.active_app)

            except Exception as e:
                print(f"Context Monitor Error: {e}")

            time.sleep(3) # Check every 3 seconds to be resource-efficient

    def get_current_context(self):
        """Returns the current safe context."""
        if self.active_app == "PRIVATE":
            return "A sensitive or private application."
        return f"Using {self.active_app} (Window: {self.active_window_title})"
