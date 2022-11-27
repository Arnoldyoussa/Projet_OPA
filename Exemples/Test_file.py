import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging

config_logging(logging, logging.DEBUG)

key = "9NoMNNgwTUU92NbtSwJSuy14z8dXVPyZQQFyEXgjgx6LvqFISaiNdGBQPPXEliSS"
secret = "rXAtGII8v290i75DsrTZKBYl0RQs7RTlwUBI8gg9YdSXNlf04ZKYAiZZOriybRqU"

spot_client = Client(key, secret)
print(spot_client.account_snapshot(type ='SPOT'))