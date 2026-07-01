from exchange.factory import create_exchange
from trade_engine.engine import TradeEngine

exchange = create_exchange("coinbase")
engine = TradeEngine(exchange)

contracts = engine.calculate_contracts(
    entry_price=58495,
    stop_price=58000,
    risk_pct=1.0,
    max_leverage=3,
)

print("=== CALCUL CONTRATS ===")
print("contracts:", contracts)
