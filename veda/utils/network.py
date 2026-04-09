import requests
import re
from urllib.parse import urlparse
from veda.utils.logger import logger

class VedaNetworkProxy:
    # Sovereign Domain Whitelist
    ALLOWED_DOMAINS = [
        "google.com", "bing.com", "wikipedia.org", "github.com",
        "stackoverflow.com", "openweathermap.org", "duckduckgo.com",
        "coingecko.com", "wttr.in"
    ]

    # Block internal/private IP ranges (SSRF Protection)
    PRIVATE_IP_REGEX = r"^(127\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.|192\.168\.)"

    @staticmethod
    def _is_authorized(url):
        """Internal helper for authorization."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if not domain: return False, "Invalid URL signature."

        # 1. Domain Check
        if not any(domain.endswith(d) for d in VedaNetworkProxy.ALLOWED_DOMAINS):
            # Check for direct IP access
            if re.match(r"^\d+\.\d+\.\d+\.\d+", domain):
                if re.match(VedaNetworkProxy.PRIVATE_IP_REGEX, domain):
                    logger.error(f"SSRF Block: Attempted access to private sector: {domain}")
                    return False, "Internal IP access restricted."
            return False, f"'{domain}' not in tactical whitelist."

        return True, "Authorized."

    @staticmethod
    def safe_get(url, timeout=15, max_size=5*1024*1024, hops=3):
        """Zero-Trust Network Access: Domain filtering and SSRF protection."""
        if hops < 0: return "Error: Maximum tactical redirection hops exceeded."
        if timeout <= 0: timeout = 1

        try:
            auth, msg = VedaNetworkProxy._is_authorized(url)
            if not auth: return f"Security Violation: {msg}"

            # 2. Size-Limited Ingress with Redirect Protection
            with requests.get(url, timeout=timeout, stream=True, allow_redirects=False) as response:
                # Manual redirect handling to maintain strict Zero-Trust per-hop
                if response.is_redirect or response.status_code in [301, 302, 303, 307, 308]:
                    redir_url = response.headers.get('Location')
                    if not redir_url: return "Error: Redirection anomaly."
                    # Fix relative redirects
                    if not redir_url.startswith('http'):
                        from urllib.parse import urljoin
                        redir_url = urljoin(url, redir_url)
                    # Recursive check with hop decrement
                    return VedaNetworkProxy.safe_get(redir_url, timeout=timeout-2, max_size=max_size, hops=hops-1)

                # Final destination authorization
                auth_final, msg_final = VedaNetworkProxy._is_authorized(response.url)
                if not auth_final:
                     logger.error(f"Sovereign Block: Unauthorized redirect to {response.url}")
                     return f"Security Violation: Redirect to unauthorized sector blocked."

                response.raise_for_status()

                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > max_size:
                    return f"Error: Payload exceeds maximum tactical limit ({max_size} bytes)."

                content = []
                total_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    total_size += len(chunk)
                    if total_size > max_size:
                        return "Error: Payload exceeded limit during transmission."
                    content.append(chunk)

                return b"".join(content).decode('utf-8', errors='ignore')

        except Exception as e:
            logger.error(f"Network Fault: {e}")
            return f"Network Error: {e}"

    @staticmethod
    def safe_post(url, json_data=None, timeout=10):
        """Zero-Trust POST implementation."""
        try:
            auth, msg = VedaNetworkProxy._is_authorized(url)
            if not auth: return f"Security Violation: {msg}"

            res = requests.post(url, json=json_data, timeout=timeout)
            res.raise_for_status()
            return res.text
        except Exception as e:
            logger.error(f"POST Network Fault: {e}")
            return f"Network Error: {e}"

    @staticmethod
    def safe_get_json(url, timeout=10):
        """Convenience method for JSON data."""
        res = VedaNetworkProxy.safe_get(url, timeout=timeout)
        if "Security Violation" in res or "Network Error" in res:
            return None
        import json
        try: return json.loads(res)
        except: return None

network = VedaNetworkProxy()
