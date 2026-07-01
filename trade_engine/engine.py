import uuid


class TradeEngine:

    def __init__(self, exchange):
        self.exchange = exchange

    def get_balance(self, currency="USDC"):
        return self.exchange.get_balance(currency)

    def get_position(self):
        return self.exchange.get_position()

    def get_open_orders(self):
        return self.exchange.get_open_orders()

    def get_protection_order(self):
        return self.exchange.get_protection_order()

    def open_long(self, contracts, stop_trigger_price, limit_price, client_order_id):
        return self.exchange.create_market_order(
            side="BUY",
            contracts=contracts,
            client_order_id=client_order_id,
            stop_trigger_price=stop_trigger_price,
            limit_price=limit_price,
        )

    def handle(self, data):
        action = data.get("action")

        handlers = {
            "OPEN_LONG": self._handle_open_long,
        }

        if action not in handlers:
            raise ValueError(f"Action non supportée : {action}")

        return handlers[action](data)

    def _handle_open_long(self, data):
        client_order_id = data.get("client_order_id")

        if client_order_id is None:
            client_order_id = f"{data.get('strategy', 'strategy')}-{uuid.uuid4()}"

        contracts = data.get("contracts")

        if contracts is None:
            contracts = 1

        return self.open_long(
            contracts=contracts,
            stop_trigger_price=data["stop_price"],
            limit_price=data["take_profit_price"],
            client_order_id=client_order_id,
        )
