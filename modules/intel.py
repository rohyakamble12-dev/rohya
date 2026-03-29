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

            results = []
            for item in soup.find_all("div", class_="result")[:3]:
                title = item.find("a", class_="result__a")
                snippet = item.find("a", class_="result__snippet")
                if title and snippet:
                    results.append(f"[{title.text.strip()}] {snippet.text.strip()}")

            if results:
                return "INTEL ACQUIRED:\n" + "\n".join(results)
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
    def get_eta(origin, destination):
        """Estimates travel time between locations using Google Maps search relay."""
        try:
            query = f"travel time from {origin} to {destination}"
            url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            # Attempt to find the duration in the search snippet
            # This is a heuristic approach for zero-API deployment
            text = soup.get_text()
            match = re.search(r"(\d+\s*(?:hr|min|hour|minute)s?)\s*(?:by|via)", text.lower())
            if match:
                return f"TACTICAL ETA: Estimated travel time from {origin} to {destination} is approximately {match.group(1)}."
            return f"TACTICAL ETA: Route analysis for {origin} to {destination} is inconclusive. Manual verification required."
        except Exception as e:
            return f"Travel link interrupted: {e}"

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

            # Simulated Trending Context
            return f"GLOBAL INTELLIGENCE BRIEF ({topic.upper()}):\n" + "\n".join([f"- {t}" for t in titles]) + "\nSTATUS: Scanning for tactical anomalies in global streams."
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
            "1. Naz Louis (YouTube/GitHub): Creator of 'Ada', specialized in blazing fast local AI and custom React-based UIs.\n"
            "2. harriik (GitHub): Developed one of the most complete 'Jarvis' clones with robust GUI and face recognition.\n"
            "3. kishanrajput23 (GitHub): Master of Python system automation for desktop assistants.\n"
            "4. PhD Security (YouTube): Known for real-world MCU tech like EDITH glasses and secure AI protocols.\n"
            "5. LiveKit: The professional framework for real-time, ultra-low latency voice interaction."
        )
