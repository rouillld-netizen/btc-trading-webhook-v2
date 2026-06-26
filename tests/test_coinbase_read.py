from json import dumps
from coinbase.rest import RESTClient
from config import COINBASE_API_KEY, COINBASE_API_SECRET

client = RESTClient(
    api_key=COINBASE_API_KEY,
    api_secret=COINBASE_API_SECRET,
)

print("=== TEST CONNEXION COINBASE ===")

print("\n=== Comptes ===")
accounts = client.get_accounts()
print(dumps(accounts.to_dict(), indent=2, ensure_ascii=False)[:3000])

print("\n=== Produits BTC / BIP ===")
products = client.get_products()
for p in products.products:
    d = p.to_dict()
    txt = f"{d.get('product_id', '')} {d.get('display_name', '')} {d.get('alias', '')}"
    if "BTC" in txt.upper() or "BIP" in txt.upper():
        print(dumps(d, indent=2, ensure_ascii=False))

print("\n=== Ordres ouverts ===")
orders = client.list_orders(order_status=["OPEN"])
print(dumps(orders.to_dict(), indent=2, ensure_ascii=False)[:3000])

print("\n=== Positions futures ===")
try:
    positions = client.get_futures_positions()
    print(dumps(positions.to_dict(), indent=2, ensure_ascii=False)[:3000])
except Exception as e:
    print("Erreur positions futures :", repr(e))
