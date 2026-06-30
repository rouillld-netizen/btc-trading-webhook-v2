from exchange.coinbase_api import CoinbaseAPI
from config import COINBASE_API_KEY, COINBASE_API_SECRET


def create_exchange(name="coinbase"):

    if name == "coinbase":
        return CoinbaseAPI(
            COINBASE_API_KEY,
            COINBASE_API_SECRET,
        )

    raise ValueError(f"Exchange non supporté : {name}")
