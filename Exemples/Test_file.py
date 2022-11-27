import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging

config_logging(logging, logging.DEBUG)


spot_client = Client()
print(spot_client.account_snapshot(type ='SPOT'))
