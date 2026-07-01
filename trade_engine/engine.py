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

        if action == "OPEN_LONG":
            return self.open_long(
                contracts=data["contracts"],
                stop_trigger_price=data["stop_price"],
                limit_price=data["take_profit_price"],
                client_order_id=data["client_order_id"],
            )

        raise ValueError(f"Action non supportée : {action}")
