import requests
from bs4 import BeautifulSoup
import wikipedia
import logging

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

    @staticmethod
    def convert_currency(amount, from_curr, to_curr):
        try:
            res = requests.get(f"https://api.exchangerate-api.com/v4/latest/{from_curr.upper()}", timeout=5)
            data = res.json()
            rate = data["rates"][to_curr.upper()]
            return f"TACTICAL EXCHANGE: {amount} {from_curr.upper()} is {round(amount * rate, 2)} {to_curr.upper()}."
        except: return "Currency link broken."

    @staticmethod
    def convert_units(value, from_unit, to_unit):
        # Basic conversions
        conversions = {
            ("c", "f"): lambda v: (v * 9/5) + 32,
            ("f", "c"): lambda v: (v - 32) * 5/9,
            ("kg", "lbs"): lambda v: v * 2.20462,
            ("lbs", "kg"): lambda v: v / 2.20462,
            ("m", "ft"): lambda v: v * 3.28084,
            ("ft", "m"): lambda v: v / 3.28084
        }
        try:
            op = conversions.get((from_unit.lower(), to_unit.lower()))
            if op: return f"UNIT CONVERSION: {value}{from_unit} is {round(op(value), 2)}{to_unit}."
            return f"Conversion from {from_unit} to {to_unit} not supported."
        except: return "Conversion protocol failed."

    @staticmethod
    def get_news(topic="technology"):
        try:
            url = f"https://news.google.com/search?q={topic}&hl=en-US&gl=US&ceid=US:en"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            titles = [t.text for t in soup.find_all("a", class_="J7YVsc")[:5]]
            if not titles: titles = [t.text for t in soup.find_all("h3")[:5]]
            return f"TACTICAL NEWS BRIEF ({topic.upper()}):\n" + "\n".join([f"- {t}" for t in titles])
        except: return "Global news relay offline."

    @staticmethod
    def get_market_data(symbol):
        """Fetches crypto/stock data using public APIs."""
        try:
            # Crypto (CoinGecko)
            res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd", timeout=5)
            data = res.json()
            if symbol.lower() in data:
                price = data[symbol.lower()]["usd"]
                return f"MARKET DATA: {symbol.upper()} is currently trading at ${price} USD."

            # Stock (Yahoo Fallback via Scraper)
            url = f"https://finance.yahoo.com/quote/{symbol.upper()}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            price = soup.find("fin-streamer", {"data-field": "regularMarketPrice"}).text
            return f"MARKET DATA: {symbol.upper()} is currently trading at ${price}."
        except: return f"Market data relay for {symbol} unavailable."

    def deep_research(self, query):
        """Summarizes multiple search results for complex queries."""
        try:
            url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            snippets = [s.text.strip() for s in soup.find_all("a", class_="result__snippet")[:3]]
            if not snippets: return self.search(query)

            combined = "\n".join(snippets)
            return f"DEEP RESEARCH REPORT: {query.upper()}\n{combined}\n--- Analysis Complete ---"
        except: return "Deep research protocols interrupted."

    @staticmethod
    def get_creator_registry():
        """Returns influential real-world creators of smart assistants."""
        return (
            "CREATOR REGISTRY (Verified Tactical Sources):\n"
            "1. harriik (GitHub): Advanced Jarvis with face/voice/GUI automation.\n"
            "2. kishanrajput23 (GitHub): Sophisticated desktop-level system control.\n"
            "3. PhD Security (YouTube): MCU-accurate Edith and secure AI architectures.\n"
            "4. The Coding Bus (YouTube): LLM-driven personalized assistant builds.\n"
            "5. LiveKit Framework: Standard for professional real-time voice agents."
        )
