import requests
from duckduckgo_search import DDGS

class WebInfo:
    @staticmethod
    def search(query):
        """Searches the web using DuckDuckGo."""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                if results:
                    summary = results[0]['body']
                    return f"According to the web: {summary}"
                return "I couldn't find anything on that."
        except Exception as e:
            return f"Search failed: {str(e)}"

    @staticmethod
    def get_weather(city="New York"):
        """Gets weather info (simplified for demo, usually needs an API key)."""
        # Using a free service that doesn't require a key or simple scraping
        try:
            url = f"https://wttr.in/{city}?format=%C+%t"
            response = requests.get(url)
            if response.status_code == 200:
                return f"The weather in {city} is {response.text}"
            return "I couldn't retrieve the weather right now."
        except Exception as e:
            return f"Weather check failed: {str(e)}"

    @staticmethod
    def get_news():
        """Gets top news headlines."""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news("top stories", max_results=3))
                if results:
                    headlines = [r['title'] for r in results]
                    return "Here are the top headlines: " + "; ".join(headlines)
                return "I couldn't find any news."
        except Exception as e:
            return f"News retrieval failed: {str(e)}"
