import requests
from bs4 import BeautifulSoup
import wikipedia

class IntelModule:
    @staticmethod
    def search(query):
        try:
            url = f"https://duckduckgo.com/html/?q={query}"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            result = soup.find("a", class_="result__a")
            return f"Intel found: {result.text}" if result else "No data matches."
        except: return "Intelligence gathering failed."

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
