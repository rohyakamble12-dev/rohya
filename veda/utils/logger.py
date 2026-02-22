import logging
import os
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler

class VedaLogger:
    def __init__(self, log_dir="logs", max_bytes=5*1024*1024, backup_count=3):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.system_log = os.path.join(log_dir, "system.json")
        self.audit_log = os.path.join(log_dir, "audit.json")

        # Setup Rotating JSON Handler for System
        self.logger = logging.getLogger("Veda")
        self.logger.setLevel(logging.INFO)

        handler = RotatingFileHandler(self.system_log, maxBytes=max_bytes, backupCount=backup_count)
        self.logger.addHandler(handler)

    def _log_json(self, level, message, **kwargs):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        log_entry.update(kwargs)
        # Use root logger for console, and our json logger for file
        json_str = json.dumps(log_entry)

        # For the file handler we just write the string
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                with open(handler.baseFilename, 'a') as f:
                    f.write(json_str + "\n")

    def info(self, message, **kwargs):
        self._log_json("INFO", message, **kwargs)

    def error(self, message, **kwargs):
        self._log_json("ERROR", message, **kwargs)

    def warning(self, message, **kwargs):
        self._log_json("WARNING", message, **kwargs)

    def audit(self, intent, params, user="User"):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "intent": intent,
            "params": params
        }
        with open(self.audit_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

# Singleton instance
logger = VedaLogger()
