import requests
import httpx
from bs4 import BeautifulSoup
from veda.features.base import VedaPlugin, PermissionTier
from veda.core.governance import governance

class ScraperPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("ingest_web", self.ingest_url, PermissionTier.SAFE,
                            permissions=["web_access"],
                            input_schema={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"], "additionalProperties": False})

        self.register_intent("fetch_url_raw", self.fetch_raw, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"], "additionalProperties": False})

    def validate_params(self, intent, params):
        url = params.get("url", "")
        if not governance.is_domain_authorized(url):
            return False, f"Governance Block: Domain for '{url}' is not in the tactical whitelist."
        return True, "Valid."

    def predict_impact(self, intent, params):
        return f"Impact: Neural ingestion of data from sector '{params.get('url', 'External')}'."

    def ingest_url(self, url_params):
        from veda.utils.network import network
        url = url_params.get("url")
        # Leverage the VedaNetworkProxy for all scraping
        content = network.safe_get(url, timeout=10)
        if content.startswith("Security Violation") or content.startswith("Network Error"):
            return content

        try:
            soup = BeautifulSoup(content, 'html.parser')
            for script in soup(["script", "style"]): script.extract()

            # Scrub context for privacy before returning to LLM
            from veda.utils.privacy import privacy
            clean_text = privacy.scrub(soup.get_text())
            return clean_text[:4000]
        except Exception as e:
            return f"Ingestion Failure: {e}"

    def fetch_raw(self, params):
        """Tactical Ingress of raw URL content."""
        import httpx
        url = params.get("url")
        try:
            with httpx.Client(follow_redirects=True, timeout=10) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.text[:4000]
        except Exception as e:
            return f"Raw Fetch Failure: {e}"
