from exchange.coinbase_api import CoinbaseAPI
from config import COINBASE_API_KEY, COINBASE_API_SECRET

coinbase = CoinbaseAPI(
    COINBASE_API_KEY,
    COINBASE_API_SECRET,
)

payload = {
    "client_order_id": "test-btc-fcm-stop-001",
    "product_id": "BIP-20DEC30-CDE",
    "side": "BUY",
    "order_configuration": {
        "marketMarketIoc": {
            "baseSize": "1"
        }
    },
    "attached_order_configuration": {
        "triggerBracketGtc": {
            "stopTriggerPrice": "58000",
            "limitPrice": "59030.00"
        }
    }
}

print("=== ORDRE RÉEL À ENVOYER ===")
print(payload)

confirm = input("Tape OUI pour envoyer l'ordre réel : ")

if confirm != "OUI":
    print("Annulé.")
    raise SystemExit

result = coinbase.create_order(payload)

print("=== RESULT ===")
print(result)
