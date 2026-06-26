from exchange.coinbase_api import CoinbaseAPI
from config import COINBASE_API_KEY, COINBASE_API_SECRET

coinbase = CoinbaseAPI(
    COINBASE_API_KEY,
    COINBASE_API_SECRET,
)

print("=== TEST BTC PERP ===")

product = coinbase.get_product("BTC-PERP-INTX")

print(product)
