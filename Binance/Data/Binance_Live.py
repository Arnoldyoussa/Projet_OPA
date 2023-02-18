from binance.client import Client

class Binance_Live:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    def exchange_info(self,symbol):
        a=self.client.get_symbol_info(symbol)
        return(a)
