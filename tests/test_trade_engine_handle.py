from exchange.factory import create_exchange
from trade_engine.engine import TradeEngine

exchange = create_exchange("coinbase")
engine = TradeEngine(exchange)

data = {
    "action": "OPEN_LONG",
    "contracts": 1,
    "stop_price": 58000,
    "take_profit_price": 59030,
    "client_order_id": "test-handle-open-long-001",
}

print("=== HANDLE TEST ===")
print(data)

confirm = input("Tape OUI pour exécuter le handle réel : ")

if confirm != "OUI":
    print("Annulé.")
    raise SystemExit

print(engine.handle(data))
