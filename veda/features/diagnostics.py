import psutil
import socket
import platform

class VedaDiagnostics:
    @staticmethod
    def get_system_health():
        """Returns a summary of system hardware health with Armor Status intelligence."""
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        swap = psutil.swap_memory()

        report = "VEDA ARMOR STATUS REPORT:\n"
        report += f"- CPU Load: {cpu_usage}% (Core Stability Nominal)\n"
        report += f"- RAM Usage: {ram.percent}% ({round(ram.available / (1024**3), 1)}GB available)\n"
        report += f"- SWAP Memory: {swap.percent}%\n"

        if battery:
            time_left = "Calculating..."
            if battery.secsleft != -1:
                hours = battery.secsleft // 3600
                minutes = (battery.secsleft % 3600) // 60
                time_left = f"{hours}h {minutes}m remaining"

            status = "CHARGING" if battery.power_plugged else "DISCHARGING"
            report += f"- Power Cell: {battery.percent}% [{status}] ({time_left})\n"

        # Top 3 Memory Consuming Processes
        report += "\nResource Intensive Protocols:\n"
        processes = []
        for proc in psutil.process_iter(['name', 'memory_percent']):
            try:
                processes.append(proc.info)
            except: pass

        top_3 = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:3]
        for p in top_3:
            report += f"› {p['name']} ({round(p['memory_percent'], 1)}%)\n"

        return report

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
