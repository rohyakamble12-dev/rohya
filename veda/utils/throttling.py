import time
from functools import wraps
from veda.utils.logger import logger

class VedaRateLimiter:
    def __init__(self):
        self.last_calls = {} # key: last_call_timestamp

    def limit(self, seconds=2.0):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = f"{args[0].__class__.__name__}.{func.__name__}"
                now = time.time()

                if key in self.last_calls:
                    elapsed = now - self.last_calls[key]
                    if elapsed < seconds:
                        wait = seconds - elapsed
                        logger.warning(f"Throttling {key}. Required wait: {wait:.2f}s")
                        return f"Strategic Pause: Please wait {wait:.1f}s before re-executing this command."

                self.last_calls[key] = now
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Global Limiter
limiter = VedaRateLimiter()
