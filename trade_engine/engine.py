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
