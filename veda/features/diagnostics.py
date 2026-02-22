import psutil
import socket
from veda.features.base import VedaPlugin, PermissionTier

class DiagnosticsPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
        self.register_intent("sys_health", self.get_system_health, PermissionTier.SAFE)
        self.register_intent("net_info", self.get_network_info, PermissionTier.SAFE)
        self.register_intent("storage_info", self.get_storage_info, PermissionTier.SAFE)

    def get_system_health(self, params):
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        report = f"VEDA ARMOR STATUS:\n- CPU: {cpu}%\n- RAM: {ram.percent}% free\n- System: Nominal"
        return report

    def get_network_info(self, params):
        try:
            hostname = socket.gethostname()
            return f"Network: {hostname} | IP: {socket.gethostbyname(hostname)}"
        except:
            return "Network diagnostic failed."

    def get_storage_info(self, params):
        usage = psutil.disk_usage('/')
        return f"Storage: {round(usage.free / (1024**3), 1)}GB free."
