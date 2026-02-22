import threading
import time
from veda.utils.logger import logger

class VedaThreadManager:
    def __init__(self):
        self.threads = {}

    def start_thread(self, name, target, args=(), daemon=True):
        """Starts and tracks a background thread."""
        if name in self.threads and self.threads[name].is_alive():
            logger.warning(f"Thread '{name}' is already running.")
            return

        thread = threading.Thread(target=target, args=args, name=name, daemon=daemon)
        self.threads[name] = thread
        thread.start()
        logger.info(f"Background process '{name}' initiated.")

    def run_with_throttle(self, name, target, interval=1.0, args=()):
        """Runs a target function in a loop with a sleep interval (throttling)."""
        def throttled_loop():
            while True:
                try:
                    target(*args)
                except Exception as e:
                    logger.error(f"Throttled loop '{name}' error: {e}")
                time.sleep(interval)

        self.start_thread(name, throttled_loop)

# Singleton manager
manager = VedaThreadManager()
