import subprocess
import re
import os

class VedaNetworkIntel:
    @staticmethod
    def scan_wifi():
        """Scans for nearby WiFi networks using Windows netsh command."""
        try:
            # Run netsh to get nearby networks
            result = subprocess.check_output(["netsh", "wlan", "show", "networks", "mode=bssid"], encoding='utf-8', errors='ignore')

            # Simple parsing of SSIDs and signal strength
            networks = []
            current_ssid = "Unknown"

            for line in result.split('\n'):
                line = line.strip()
                if line.startswith("SSID"):
                    current_ssid = line.split(":")[1].strip()
                elif "Signal" in line:
                    signal = line.split(":")[1].strip()
                    networks.append(f"{current_ssid} ({signal})")

            if not networks:
                return "I couldn't detect any nearby wireless networks. Ensure your WiFi adapter is active."

            return "Nearby Wireless Networks detected:\n" + "\n".join(networks[:10])
        except Exception as e:
            return f"WiFi scan failed: {str(e)}"

    @staticmethod
    def recover_stored_passwords():
        """Retrieves passwords for WiFi networks previously saved on this machine."""
        try:
            # 1. Get all profiles
            profiles_data = subprocess.check_output(["netsh", "wlan", "show", "profiles"], encoding='utf-8', errors='ignore')
            profiles = re.findall(r"All User Profile\s*:\s*(.*)", profiles_data)

            results = []
            for name in profiles:
                name = name.strip()
                try:
                    # 2. Get password for each profile
                    pass_data = subprocess.check_output(["netsh", "wlan", "show", "profile", name, "key=clear"], encoding='utf-8', errors='ignore')
                    password_match = re.search(r"Key Content\s*:\s*(.*)", pass_data)
                    password = password_match.group(1).strip() if password_match else "None (Open or Enterprise)"
                    results.append(f"Network: {name} | Key: {password}")
                except:
                    results.append(f"Network: {name} | Key: [Failed to Retrieve]")

            if not results:
                return "No stored WiFi profiles found on this PC."

            return "Security Audit: Stored WiFi Credentials:\n" + "\n".join(results)
        except Exception as e:
            return f"Credential recovery failed: {str(e)}"

    @staticmethod
    def scan_bluetooth():
        """Attempts to list paired bluetooth devices (Simplified)."""
        try:
            # Bleak is better for scanning, but for a standard Win shell:
            result = subprocess.check_output(["powershell", "Get-PnpDevice -Class Bluetooth | Select-Object FriendlyName"], encoding='utf-8', errors='ignore')
            return "Paired / Detected Bluetooth Devices:\n" + result.strip()
        except:
            return "Bluetooth discovery is restricted on this environment."
