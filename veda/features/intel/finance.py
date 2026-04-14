try:
    from veda.features.web_info import WebPlugin
except ImportError:
    WebPlugin = None

class VedaFinance:
    @staticmethod
    def get_market_info(symbol):
        """Fetches market info for a stock or crypto symbol."""
        if not WebPlugin: return "Strategic Web Access Offline."
        query = f"current price of {symbol}"
        # Leverage existing search capability
        try:
            plugin = WebPlugin(None)
            result = plugin.search({"query": query})
            return result
        except: return "Finance node failure."

    @staticmethod
    def get_crypto_price(coin):
        """Fetches crypto price."""
        if not WebPlugin: return "Strategic Web Access Offline."
        query = f"{coin} price today"
        try:
            plugin = WebPlugin(None)
            return plugin.search({"query": query})
        except: return "Crypto node failure."
