import requests
from bs4 import BeautifulSoup
import wikipedia

class IntelModule:
    @staticmethod
    def search(query):
        if not query: return "Query required for intelligence search."
        try:
            url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            res = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            result = soup.find("a", class_="result__a")
            if result:
                snippet = soup.find("a", class_="result__snippet")
                text = snippet.text if snippet else result.text
                return f"Intel found: {text.strip()}"
            return "No matching records in global search database."
        except Exception as e:
            return f"Intelligence gathering interrupted: {e}"

    @staticmethod
    def get_wiki(topic):
        try:
            return wikipedia.summary(topic, sentences=2)
        except: return "Topic not found in global databases."

    @staticmethod
    def get_weather(city):
        try:
            res = requests.get(f"https://wttr.in/{city}?format=3")
            return res.text.strip()
        except: return "Weather link broken."
