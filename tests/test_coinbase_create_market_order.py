from exchange.coinbase_api import CoinbaseAPI
from config import COINBASE_API_KEY, COINBASE_API_SECRET

coinbase = CoinbaseAPI(
    COINBASE_API_KEY,
    COINBASE_API_SECRET,
)

print("=== CREATE MARKET ORDER FUNCTION ===")

confirm = input("Tape OUI pour envoyer un ordre réel BUY avec stop : ")

if confirm != "OUI":
    print("Annulé.")
    raise SystemExit

result = coinbase.create_market_order(
    side="BUY",
    contracts=1,
    client_order_id="test-create-market-order-001",
    stop_trigger_price=58000,
    limit_price=59030,
)

print(result)
