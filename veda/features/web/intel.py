from veda.features.base import VedaPlugin, PermissionTier
from veda.utils.network import network

class WebIntelPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("weather", self.get_weather, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"city": {"type": "string", "maxLength": 50}}})
        self.register_intent("stock_price", self.get_market_info, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"symbol": {"type": "string", "maxLength": 10}}, "required": ["symbol"]})
        self.register_intent("crypto_price", self.get_market_info, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"coin": {"type": "string", "maxLength": 20}}, "required": ["coin"]})

    def get_weather(self, params):
        city = params.get("city", "auto")
        url = f"https://wttr.in/{city}?format=%C+%t"
        res_text = network.safe_get(url, timeout=5)
        if "Network Error" in res_text: return "Orbital sensors failing to report weather."
        return f"Atmospheric status ({city}): {res_text}"

    def get_market_info(self, params):
        symbol = params.get("symbol") or params.get("coin") or "market"
        web_search = self.assistant.plugins.get_plugin("WebSearchPlugin")
        if web_search:
            return web_search.search({"query": f"current price of {symbol}"})
        return "Financial intelligence link offline."
