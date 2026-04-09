import requests
import httpx
import xml.etree.ElementTree as ET
import asyncio
import re
import webbrowser
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

        self.register_intent("world_briefing", self.get_world_briefing, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})

        self.register_intent("fetch_url", self.fetch_url, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"], "additionalProperties": False})

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
                results = list(ddgs.text(query, max_results=3))
                if results: return results[0]['body']
                return "Zero matches."
        except Exception as e:
            return f"Strategic Link Failure: {e}"

    def get_weather(self, params):
        from veda.utils.network import network
        city = params.get("city", "auto")
        url = f"https://wttr.in/{city}?format=%C+%t"
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

    async def _fetch_rss_feed(self, client, url):
        """Tactical RSS Ingress."""
        try:
            response = await client.get(url, headers={'User-Agent': 'Veda-AI/1.1'}, timeout=5.0)
            if response.status_code != 200: return []
            root = ET.fromstring(response.content)
            source = url.split('.')[1].upper()
            items = []
            for item in root.findall(".//item")[:3]:
                title = item.findtext("title")
                desc = item.findtext("description")
                if desc: desc = re.sub('<[^<]+?>', '', desc).strip()
                items.append(f"[{source}] {title}: {desc[:100]}...")
            return items
        except Exception: return []

    def get_world_briefing(self, params):
        """Parallel Global News Briefing."""
        feeds = [
            'https://feeds.bbci.co.uk/news/world/rss.xml',
            'https://www.cnbc.com/id/100727362/device/rss/rss.html',
            'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
            'https://www.aljazeera.com/xml/rss/all.xml'
        ]

        async def _gather():
            async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                tasks = [self._fetch_rss_feed(client, url) for url in feeds]
                results = await asyncio.gather(*tasks)
                flat = [item for sub in results for item in sub]
                return "\n".join(flat[:10]) if flat else "Global news grid unresponsive."

        try:
            new_loop = asyncio.new_event_loop()
            return new_loop.run_until_complete(_gather())
        except Exception as e:
            return f"Intel failure: {e}"

    def get_market_info(self, params):
        symbol = params.get("symbol") or params.get("coin") or "market"
        try:
             from veda.utils.network import network
             if params.get("coin"):
                 url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
                 data = network.safe_get_json(url)
                 if data and symbol.lower() in data:
                     return f"Current value for {symbol}: ${data[symbol.lower()]['usd']}"
             return self.search({"query": f"current price of {symbol}"})
        except:
             return self.search({"query": f"current price of {symbol}"})

    def fetch_url(self, params):
        """Strategic Ingress: Fetches raw content from a URL."""
        from veda.utils.network import network
        url = params.get("url")
        if not url: return "URL required."
        content = network.safe_get(url, timeout=10)
        return content[:4000]
