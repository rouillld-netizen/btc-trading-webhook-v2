from pathlib import Path
from dotenv import dotenv_values

BASE_DIR = Path(__file__).resolve().parent
env = dotenv_values(BASE_DIR / ".env")

COINBASE_API_KEY = env.get("COINBASE_API_KEY")

_coinbase_private_key_file = env.get("COINBASE_PRIVATE_KEY_FILE")
COINBASE_API_SECRET = (
    (BASE_DIR / _coinbase_private_key_file).read_text()
    if _coinbase_private_key_file
    else None
)

BINANCE_API_KEY = env.get("BINANCE_API_KEY")
BINANCE_API_SECRET = env.get("BINANCE_API_SECRET")

WEBHOOK_SECRET = env.get("WEBHOOK_SECRET")
PUSHOVER_USER_KEY = env.get("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = env.get("PUSHOVER_API_TOKEN")
