from veda.features.base import VedaPlugin, PermissionTier
from veda.utils.throttling import limiter
from duckduckgo_search import DDGS
import webbrowser
import urllib.parse

class WebSearchPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("web_search", self.search, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"query": {"type": "string", "maxLength": 200}}, "required": ["query"]})
        self.register_intent("web_find", self.web_find, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]})

    @limiter.limit(3.0)
    def search(self, params):
        query = params.get("query", "")
        if not query: return "Search topic required."
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                if results: return results[0]['body']
                return "Zero matches."
        except Exception as e: return f"Strategic Link Failure: {e}"

    def web_find(self, params):
        query = params.get('query', '')
        safe_query = urllib.parse.quote(query)
        webbrowser.open(f"https://www.google.com/search?q={safe_query}")
        return "Searching..."
