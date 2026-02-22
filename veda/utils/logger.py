import logging
import os
from datetime import datetime

class VedaLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # General System Log
        self.system_log = os.path.join(log_dir, "system.log")
        # Audit Trail (Security/Actions)
        self.audit_log = os.path.join(log_dir, "audit.log")

        logging.basicConfig(
            filename=self.system_log,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )
        self.logger = logging.getLogger("Veda")

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def audit(self, intent, params, user="User"):
        """Records a permanent record of a system action."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {user} -> INTENT: {intent} | PARAMS: {params}\n"
        with open(self.audit_log, "a") as f:
            f.write(log_entry)
        self.info(f"AUDIT: {intent} executed.")

    def get_last_audit(self, count=10):
        try:
            if not os.path.exists(self.audit_log): return []
            with open(self.audit_log, "r") as f:
                return f.readlines()[-count:]
        except:
            return []

# Singleton instance
logger = VedaLogger()
