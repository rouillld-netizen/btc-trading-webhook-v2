from exchange.coinbase_api import CoinbaseAPI
from config import COINBASE_API_KEY, COINBASE_API_SECRET

coinbase = CoinbaseAPI(
    COINBASE_API_KEY,
    COINBASE_API_SECRET,
)

protection_order = coinbase.get_protection_order()

print("=== ORDRE DE PROTECTION ===")
print(protection_order)

confirm = input("Tape OUI pour annuler l'ordre de protection : ")

if confirm != "OUI":
    print("Annulé.")
    raise SystemExit

print(coinbase.cancel_protection_order())
