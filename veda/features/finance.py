import requests

class FinancePlugin:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "market_data": self.get_market_stats
        }

    def get_market_stats(self, params):
        asset = params.get("asset", "bitcoin").lower()
        try:
            # Using CoinGecko open API for crypto data
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset}&vs_currencies=usd&include_24hr_change=true"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if asset in data:
                    price = data[asset]['usd']
                    change = data[asset].get('usd_24h_change', 0)
                    return f"Market Intelligence for {asset.upper()}: ${price:,} (24h Change: {change:.2f}%)"
            return f"Asset '{asset}' not found in active market link."
        except Exception as e:
            return f"Market link unstable: {e}"
