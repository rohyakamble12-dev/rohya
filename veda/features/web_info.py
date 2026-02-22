import requests
from duckduckgo_search import DDGS
from veda.features.base import VedaPlugin, PermissionTier

class WebPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
        self.register_intent("web_search", self.search, PermissionTier.SAFE)
        self.register_intent("weather", self.get_weather, PermissionTier.SAFE)
        self.register_intent("get_news", self.get_news, PermissionTier.SAFE)
        self.register_intent("stock_price", self.get_market_info, PermissionTier.SAFE)
        self.register_intent("crypto_price", self.get_market_info, PermissionTier.SAFE)

    def search(self, params):
        query = params.get("query", "")
        if not query: return "Please specify what to search for."
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                if results:
                    return f"Search result: {results[0]['body']}"
                return "No results found."
        except Exception as e:
            return f"Search failed: {e}"

    def get_weather(self, params):
        city = params.get("city", "auto")
        try:
            url = f"https://wttr.in/{city}?format=%C+%t"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return f"Weather in {city}: {response.text}"
            return "Weather data unavailable."
        except Exception as e:
            return f"Weather check failed: {e}"

    def get_news(self, params):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news("world news", max_results=3))
                if results:
                    headlines = [r['title'] for r in results]
                    return "Top stories: " + " | ".join(headlines)
                return "No news found."
        except Exception as e:
            return f"News retrieval failed: {e}"

    def get_market_info(self, params):
        symbol = params.get("symbol") or params.get("coin") or "market"
        query = f"current price of {symbol}"
        return self.search({"query": query})
