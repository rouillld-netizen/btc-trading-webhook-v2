from exchange.coinbase_api import CoinbaseAPI
from config import COINBASE_API_KEY, COINBASE_API_SECRET

coinbase = CoinbaseAPI(
    COINBASE_API_KEY,
    COINBASE_API_SECRET,
)

print("=== OPEN LONG WITH STOP ===")

result = coinbase.open_long_with_stop(
    contracts=1,
    stop_trigger_price=58000,
    limit_price=59030,
    client_order_id="test-open-long-stop-fn-001",
)

print(result)
