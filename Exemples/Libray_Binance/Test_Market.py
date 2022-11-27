from binance.spot import Spot 

client = Spot()

# Get server timestamp
print(client.time())
# Get klines of BTCUSDT at 1m interval
#print(client.klines("BTCUSDT", "1m"))
# Get last 10 klines of BNBUSDT at 1h interval
print(client.klines("BNBBTC", "4h", limit=10))