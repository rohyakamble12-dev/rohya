import requests
from duckduckgo_search import DDGS

class WebInfo:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "web_search": self.web_search,
            "weather": self.get_weather,
            "news": self.get_news
        }

    def web_search(self, params):
        query = params.get("query")
        try:
            with DDGS() as ddgs:
                res = list(ddgs.text(query, max_results=1))
                return f"Web result: {res[0]['body']}" if res else "No results found."
        except: return "Search failed."

    def get_weather(self, params):
        city = params.get("city", "New York")
        try:
            res = requests.get(f"https://wttr.in/{city}?format=%C+%t")
            return f"Weather in {city}: {res.text}" if res.status_code == 200 else "Weather unavailable."
        except: return "Weather error."

    def get_news(self, params=None):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news("top headlines", max_results=3))
                if results:
                    headlines = [r['title'] for r in results]
                    return "Tactical update: " + "; ".join(headlines)
                return "No news available at this moment."
        except: return "Intelligence gathering failed."
