from exchange.coinbase_api import CoinbaseAPI
from config import COINBASE_API_KEY, COINBASE_API_SECRET

coinbase = CoinbaseAPI(
    COINBASE_API_KEY,
    COINBASE_API_SECRET,
)

print("=== TEST PRODUITS BTC ===")

products = coinbase.get_products({
    "product_type": "FUTURE",
    "contract_expiry_type": "PERPETUAL",
})

for p in products.get("products", []):
    txt = f"{p.get('product_id','')} | {p.get('display_name','')} | {p.get('product_type','')} | {p.get('product_venue','')}"
    if "BTC" in txt.upper() or "BIP" in txt.upper():
        print(txt)
