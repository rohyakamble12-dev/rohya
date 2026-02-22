import psutil
import socket
from veda.features.base import VedaPlugin, PermissionTier

class DiagnosticsPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("sys_health", self.get_system_health, PermissionTier.SAFE)
        self.register_intent("net_info", self.get_network_info, PermissionTier.SAFE)
        self.register_intent("storage_info", self.get_storage_info, PermissionTier.SAFE)

    def get_system_health(self, params):
        return f"Armor status: CPU {psutil.cpu_percent()}% | RAM {psutil.virtual_memory().percent}%."

    def get_network_info(self, params):
        return f"Network: {socket.gethostname()} | IP: {socket.gethostbyname(socket.gethostname())}"

    def get_storage_info(self, params):
        u = psutil.disk_usage('/')
        return f"Storage: {round(u.free / (1024**3), 1)}GB available."
