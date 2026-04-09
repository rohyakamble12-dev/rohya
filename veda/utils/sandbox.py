import os
import re
import subprocess
from veda.utils.logger import logger

class VedaSandbox:
    @staticmethod
    def sanitize_path(path, base_dirs=None):
        """Absolute Sovereign Path-Jail: Enforces absolute normalization and sector boundaries."""
        if not path: return None

        # 1. Expand and Normalize
        try:
            normalized_path = os.path.abspath(os.path.expanduser(str(path)))
        except Exception: return None

        # 2. Block sensitive system paths
        forbidden = [
            r"C:\\Windows", r"C:\\Program Files", r"C:\\Users\\[^\\]+\\AppData",
            r"/etc", r"/var", r"/root", r"/bin", r"/sbin"
        ]
        for pattern in forbidden:
            if re.search(pattern, normalized_path, re.IGNORECASE):
                logger.error(f"Sovereign Block: Unauthorized access to system sector: {normalized_path}")
                return None

        # 3. Sector Enforcement
        if base_dirs:
            authorized = False
            for b in base_dirs:
                b_abs = os.path.abspath(os.path.expanduser(b))
                if normalized_path.startswith(b_abs):
                    authorized = True
                    break
            if not authorized:
                logger.error(f"Sovereign Block: Path '{normalized_path}' is outside tactical sectors.")
                return None

        return normalized_path

    @staticmethod
    def filter_app_name(name):
        """Strategic app name filtering."""
        if not name: return ""
        return re.sub(r'[^a-zA-Z0-9\s.-]', '', str(name)).strip()

class SovereignShell:
    # Hard-coded Tactical Whitelist
    ALLOWED_COMMANDS = {
        "ipconfig": r"^ipconfig(/all)?$",
        "ping": r"^ping\s+[\w.-]+$",
        "systeminfo": r"^systeminfo$",
        "netstat": r"^netstat\s+-an$",
        "tasklist": r"^tasklist$",
        "whoami": r"^whoami$",
        "dir": r"^dir(?:\s+[\w\\.:\-\"]+)?$",
        "tracert": r"^tracert\s+[\w.-]+$",
        "nslookup": r"^nslookup\s+[\w.-]+$",
        "getmac": r"^getmac$"
    }

    @staticmethod
    def execute(command_string, timeout=10):
        """Zero-Trust Shell: Regex-based whitelist enforcement with no shell=True."""
        import shlex
        try:
            cmd_parts = shlex.split(command_string)
        except ValueError as e:
            return f"Security Violation: Malformed shell sequence: {e}"

        if not cmd_parts: return "Error: Null command."

        base_cmd = cmd_parts[0].lower()
        if base_cmd not in SovereignShell.ALLOWED_COMMANDS:
            return f"Security Violation: Command '{base_cmd}' is not in the tactical whitelist."

        # Regex validation for the full command string
        pattern = SovereignShell.ALLOWED_COMMANDS[base_cmd]
        if not re.match(pattern, command_string.strip(), re.IGNORECASE):
            return f"Security Violation: Malformed or unauthorized arguments for '{base_cmd}'."

        try:
            # Physically isolated execution via subprocess
            res = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=timeout, shell=False)
            if res.returncode == 0:
                return res.stdout.strip() or "Sequence Success."
            return f"Tactical Error: {res.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return f"Tactical Timeout: Sequence aborted after {timeout}s."
        except Exception as e:
            return f"Tactical Fault: {e}"

# Global Sandbox Utility
sandbox = VedaSandbox()
shell = SovereignShell()
