from abc import ABC, abstractmethod


class ExchangeAdapter(ABC):

    @abstractmethod
    def get_balance(self, currency="USDC"):
        pass

    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def get_open_orders(self):
        pass

    @abstractmethod
    def create_market_order(self, side, contracts, client_order_id, stop_trigger_price=None, limit_price=None):
        pass

    @abstractmethod
    def get_protection_order(self):
        pass

    @abstractmethod
    def cancel_protection_order(self):
        pass
