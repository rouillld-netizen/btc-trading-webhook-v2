from exchange.coinbase_api import CoinbaseAPI
from config import COINBASE_API_KEY, COINBASE_API_SECRET

coinbase = CoinbaseAPI(
    COINBASE_API_KEY,
    COINBASE_API_SECRET,
)

print("=== ORDRES ===")

orders = coinbase.get_orders()

print(orders)

