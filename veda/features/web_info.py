import requests
from duckduckgo_search import DDGS
from veda.features.base import VedaPlugin, PermissionTier
from veda.utils.throttling import limiter

class WebPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("web_search", self.search, PermissionTier.SAFE)
        self.register_intent("weather", self.get_weather, PermissionTier.SAFE)
        self.register_intent("get_news", self.get_news, PermissionTier.SAFE)
        self.register_intent("stock_price", self.get_market_info, PermissionTier.SAFE)
        self.register_intent("crypto_price", self.get_market_info, PermissionTier.SAFE)

    @limiter.limit(3.0)
    def search(self, params):
        query = params.get("query", "")
        if not query: return "Search topic required."
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                if results: return results[0]['body']
                return "Zero matches."
        except Exception as e:
            return f"DDG Link failure: {e}"

    def get_weather(self, params):
        city = params.get("city", "auto")
        try:
            res = requests.get(f"https://wttr.in/{city}?format=%C+%t", timeout=5)
            return f"Atmospheric status ({city}): {res.text}"
        except:
            return "Unable to sync with orbital weather sensors."

    def get_news(self, params):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news("world", max_results=3))
                return "Headlines: " + " | ".join([r['title'] for r in results])
        except: return "Global intel feed offline."

    def get_market_info(self, params):
        symbol = params.get("symbol") or params.get("coin") or "market"
        return self.search({"query": f"current price of {symbol}"})
