import requests
from duckduckgo_search import DDGS
from veda.features.base import VedaPlugin, PermissionTier
from veda.utils.throttling import limiter

class WebPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("web_search", self.search, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"query": {"type": "string", "maxLength": 200}}, "required": ["query"], "additionalProperties": False})

        self.register_intent("weather", self.get_weather, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"city": {"type": "string", "maxLength": 50}}, "additionalProperties": False})

        self.register_intent("get_news", self.get_news, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})

        self.register_intent("stock_price", self.get_market_info, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"symbol": {"type": "string", "maxLength": 10}}, "required": ["symbol"], "additionalProperties": False})

        self.register_intent("crypto_price", self.get_market_info, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"coin": {"type": "string", "maxLength": 20}}, "required": ["coin"], "additionalProperties": False})

    @limiter.limit(3.0)
    def search(self, params):
        query = params.get("query", "")
        if not query: return "Search topic required."
        try:
            with DDGS() as ddgs:
                # Add strict timeout via proxy or library if possible, otherwise rely on requests if it uses it
                results = list(ddgs.text(query, max_results=3))
                if results: return results[0]['body']
                return "Zero matches."
        except Exception as e:
            return f"Strategic Link Failure: {e}"

    def get_weather(self, params):
        from veda.utils.network import network
        city = params.get("city", "auto")
        url = f"https://wttr.in/{city}?format=%C+%t"

        # Security: Use proxy for weather ingress
        res_text = network.safe_get(url, timeout=5)
        if "Security Violation" in res_text: return res_text

        if "Network Error" in res_text:
            return "Orbital sensors failing to report weather."

        return f"Atmospheric status ({city}): {res_text}"

    def get_news(self, params):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news("world", max_results=3))
                return "Global Intel: " + " | ".join([r['title'] for r in results])
        except Exception as e: return "Intel feed disconnected."

    def get_market_info(self, params):
        symbol = params.get("symbol") or params.get("coin") or "market"
        try:
             # Use a more direct API for finance to be functional
             from veda.utils.network import network
             if params.get("coin"):
                 url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
                 data = network.safe_get_json(url)
                 if data and symbol.lower() in data:
                     return f"Current value for {symbol}: ${data[symbol.lower()]['usd']}"
             else:
                 # Standard stock via search for simplicity as we lack yfinance in requirements
                 return self.search({"query": f"current price of {symbol}"})
        except:
             return self.search({"query": f"current price of {symbol}"})
