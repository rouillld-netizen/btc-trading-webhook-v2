from exchange.coinbase_api import CoinbaseAPI
from config import COINBASE_API_KEY, COINBASE_API_SECRET

coinbase = CoinbaseAPI(
    COINBASE_API_KEY,
    COINBASE_API_SECRET,
)

payload = {
    "product_id": "BIP-20DEC30-CDE",
    "side": "BUY",
    "commission_rate": {},
    "order_configuration": {
        "marketMarketIoc": {
            "baseSize": "1"
        }
    },
    "skip_fcm_risk_check": True
}

print("=== PREVIEW ORDER ===")
print(payload)

result = coinbase.preview_order(payload)

print("=== RESULT ===")
print(result)
