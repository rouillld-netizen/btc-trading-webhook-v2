from exchange.factory import create_exchange
from trade_engine.engine import TradeEngine

exchange = create_exchange("coinbase")
engine = TradeEngine(exchange)

print("=== TRADE ENGINE ===")
print("Balance:", engine.get_balance())
print("Position:", engine.get_position())
print("Protection:", engine.get_protection_order())
