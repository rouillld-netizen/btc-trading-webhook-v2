from exchange.factory import create_exchange

exchange = create_exchange("coinbase")

position = exchange.get_position()
protection = exchange.get_protection_order()

print("=== POSITION ===")
print(position)

print("=== PROTECTION ACTUELLE ===")
print(protection)

confirm = input("Tape OUI pour créer un nouvel ordre de protection SELL : ")

if confirm != "OUI":
    print("Annulé.")
    raise SystemExit

result = exchange.create_protection_order(
    side="SELL",
    contracts=position["contracts"],
    stop_trigger_price=58000,
    limit_price=61000,
    client_order_id="test-protection-full-position-001",
)

print(result)
