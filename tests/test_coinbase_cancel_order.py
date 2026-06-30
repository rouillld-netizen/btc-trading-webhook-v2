from exchange.coinbase_api import CoinbaseAPI
from config import COINBASE_API_KEY, COINBASE_API_SECRET

coinbase = CoinbaseAPI(
    COINBASE_API_KEY,
    COINBASE_API_SECRET,
)

open_orders = coinbase.get_open_orders()

print("=== ORDRES OUVERTS ===")
print(open_orders)

if not open_orders:
    print("Aucun ordre ouvert.")
    raise SystemExit

order_id = open_orders[0]["order_id"]

confirm = input(f"Tape OUI pour annuler l'ordre {order_id} : ")

if confirm != "OUI":
    print("Annulé.")
    raise SystemExit

print(coinbase.cancel_order(order_id))
