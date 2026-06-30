from exchange.coinbase_api import CoinbaseAPI
from config import COINBASE_API_KEY, COINBASE_API_SECRET

coinbase = CoinbaseAPI(
    COINBASE_API_KEY,
    COINBASE_API_SECRET,
)

payload = {
    "client_order_id": "test-close-001",
    "product_id": "BIP-20DEC30-CDE",
    "side": "SELL",
    "order_configuration": {
        "marketMarketIoc": {
            "baseSize": "1"
        }
    }
}

print("=== FERMETURE POSITION ===")
print(payload)

confirm = input("Tape OUI pour fermer la position : ")

if confirm != "OUI":
    print("Annulé.")
    raise SystemExit

result = coinbase.create_order(payload)

print(result)
