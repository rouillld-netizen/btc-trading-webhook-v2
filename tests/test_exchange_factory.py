from exchange.factory import create_exchange

exchange = create_exchange("coinbase")

print("=== FACTORY ===")
print(exchange.get_position())
