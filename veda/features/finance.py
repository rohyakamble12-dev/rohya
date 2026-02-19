from veda.features.web_info import WebInfo

class VedaFinance:
    @staticmethod
    def get_market_info(symbol):
        """Fetches market info for a stock or crypto symbol."""
        query = f"current price of {symbol}"
        # Leverage existing search capability
        result = WebInfo.search(query)
        return result

    @staticmethod
    def get_crypto_price(coin):
        """Fetches crypto price."""
        query = f"{coin} price today"
        return WebInfo.search(query)
