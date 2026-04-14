from veda.features.base import VedaPlugin, PermissionTier
from duckduckgo_search import DDGS
import httpx
import xml.etree.ElementTree as ET
import asyncio
import re

class NewsPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("get_news", self.get_news, PermissionTier.SAFE)
        self.register_intent("world_briefing", self.get_world_briefing, PermissionTier.SAFE)

    def get_news(self, params):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news("world", max_results=3))
                return "Global Intel: " + " | ".join([r['title'] for r in results])
        except Exception as e: return "Intel feed disconnected."

    async def _fetch_rss_feed(self, client, url):
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
            loop = asyncio.new_event_loop()
            return loop.run_until_complete(_gather())
        except Exception as e: return f"Intel failure: {e}"
