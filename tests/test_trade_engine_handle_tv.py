from exchange.factory import create_exchange
from trade_engine.engine import TradeEngine

exchange = create_exchange("coinbase")
engine = TradeEngine(exchange)

data = {
    "action": "OPEN_LONG",
    "symbol": "BTC-USDC",
    "strategy": "BTC_H1",
    "timeframe": "1H",
    "risk_pct": 1.0,
    "entry_price": 58495,
    "stop_price": 58000,
    "take_profit_price": 61000,
    "max_leverage": 3,
    "notify": True,
}

print("=== HANDLE TRADINGVIEW FORMAT ===")
print(data)

confirm = input("Tape OUI pour exécuter un vrai OPEN_LONG : ")

if confirm != "OUI":
    print("Annulé.")
    raise SystemExit

print(engine.handle(data))
