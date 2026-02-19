import psutil
import socket
import platform

class VedaDiagnostics:
    @staticmethod
    def get_system_health():
        """Returns a summary of system hardware health."""
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        battery = psutil.sensors_battery()

        health_report = f"System Health Report:\n- CPU Usage: {cpu_usage}%\n- RAM Usage: {ram.percent}%"

        if battery:
            health_report += f"\n- Battery: {battery.percent}% ({'Charging' if battery.power_plugged else 'Discharging'})"

        return health_report

    @staticmethod
    def get_network_info():
        """Returns local and public network information."""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return f"Network Status:\n- Hostname: {hostname}\n- Local IP: {local_ip}\n- Connection: Stable"
        except Exception as e:
            return f"Failed to retrieve network info: {str(e)}"

    @staticmethod
    def get_storage_info():
        """Checks disk space."""
        usage = psutil.disk_usage('/')
        free_gb = round(usage.free / (1024**3), 2)
        total_gb = round(usage.total / (1024**3), 2)
        return f"Storage Info: {free_gb} GB free out of {total_gb} GB."
