from exchange.coinbase_api import CoinbaseAPI
from config import COINBASE_API_KEY, COINBASE_API_SECRET

coinbase = CoinbaseAPI(
    COINBASE_API_KEY,
    COINBASE_API_SECRET,
)

payload = {
    "product_id": "BTC-PERP-INTX",
    "side": "BUY",
    "order_configuration": {
        "market_market_ioc": {
            "base_size": "1"
        }
    }
}

print("=== PREVIEW ORDER ===")
print(payload)

result = coinbase.preview_order(payload)

print("=== RESULT ===")
print(result)
