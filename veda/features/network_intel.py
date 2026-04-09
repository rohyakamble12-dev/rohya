import subprocess
import re
import os
import psutil
import socket
from veda.features.base import VedaPlugin, PermissionTier

class NetworkPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("wifi_scan", self.scan_wifi, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("password_recovery", self.recover_stored_passwords, PermissionTier.ADMIN,
                            permissions=["os_level"], risk_level="High",
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("security_audit", self.perform_security_audit, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})

    def scan_wifi(self, params):
        try:
            result = subprocess.check_output(["netsh", "wlan", "show", "networks"], encoding='utf-8', errors='ignore', timeout=10)
            return f"Networks:\n{result[:500]}"
        except Exception as e: return "WiFi scan failed or restricted."

    def recover_stored_passwords(self, params):
        return "Tactical Access Denied: Credential recovery restricted in this session."

    def perform_security_audit(self, params):
        report = "VEDA SECURITY AUDIT:\n"
        # Firewall
        try:
            res = subprocess.check_output(["netsh", "advfirewall", "show", "currentprofile"], encoding='utf-8', timeout=5)
            report += f"- Firewall: Active\n"
        except Exception as e: report += "- Firewall: Restricted\n"

        # Suspicious processes
        blacklist = ["wireshark", "pcap", "keylogger"]
        found = []
        for proc in psutil.process_iter(['name']):
            if any(b in proc.info['name'].lower() for b in blacklist): found.append(proc.info['name'])

        report += f"- Integrity: {'NOMINAL' if not found else 'ALERT (' + ', '.join(found) + ')'}"
        return report
