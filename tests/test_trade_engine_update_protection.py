from exchange.factory import create_exchange
from trade_engine.engine import TradeEngine

exchange = create_exchange("coinbase")
engine = TradeEngine(exchange)

data = {
    "action": "UPDATE_PROTECTION",
    "strategy": "BTC_H1",
    "stop_price": 58100,
    "take_profit_price": 61000,
}

print("=== UPDATE PROTECTION ===")
print(data)

confirm = input("Tape OUI pour modifier réellement la protection : ")

if confirm != "OUI":
    print("Annulé.")
    raise SystemExit

print(engine.handle(data))
