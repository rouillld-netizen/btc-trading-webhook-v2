import uuid
from decimal import Decimal, ROUND_DOWN

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
            "UPDATE_PROTECTION": self._handle_update_protection,
        }

        if action not in handlers:
            raise ValueError(f"Action non supportée : {action}")

        return handlers[action](data)

    def _handle_open_long(self, data):
        position = self.get_position()

        if position is not None and data.get("pyramiding") is not True:
            return {
                "status": "ignored",
                "reason": "Position déjà ouverte et pyramidage non autorisé.",
                "position": position,
            }        
        client_order_id = data.get("client_order_id")

        if client_order_id is None:
            client_order_id = f"{data.get('strategy', 'strategy')}-{uuid.uuid4()}"

        contracts = data.get("contracts")

        if contracts is None:
            contracts = self.calculate_contracts(
                entry_price=data["entry_price"],
                stop_price=data["stop_price"],
                risk_pct=data["risk_pct"],
                max_leverage=data["max_leverage"],
            )

        return self.open_long(
            contracts=contracts,
            stop_trigger_price=data["stop_price"],
            limit_price=data["take_profit_price"],
            client_order_id=client_order_id,
        )

    def calculate_contracts(self, entry_price, stop_price, risk_pct, max_leverage):
        balance = self.get_balance("USDC")

        capital = Decimal(balance["available"])
        entry = Decimal(str(entry_price))
        stop = Decimal(str(stop_price))
        risk_pct = Decimal(str(risk_pct))
        max_leverage = Decimal(str(max_leverage))

        contract_size_btc = Decimal("0.01")

        risk_amount = capital * risk_pct / Decimal("100")
        risk_per_contract = abs(entry - stop) * contract_size_btc

        if risk_per_contract <= 0:
            raise ValueError("Distance au stop invalide")

        contracts_by_risk = risk_amount / risk_per_contract

        notional_per_contract = entry * contract_size_btc
        contracts_by_leverage = (capital * max_leverage) / notional_per_contract

        contracts = min(contracts_by_risk, contracts_by_leverage)
        contracts = contracts.to_integral_value(rounding=ROUND_DOWN)

        if contracts < 1:
            contracts = Decimal("1")

        return int(contracts)

    def _handle_update_protection(self, data):
        position = self.get_position()

        if position is None:
            return {
                "status": "ignored",
                "reason": "Aucune position ouverte.",
            }

        protection = self.get_protection_order()

        if protection is not None:
            current_config = protection.get("configuration", {}).get("trigger_bracket_gtc", {})

            current_stop = str(current_config.get("stop_trigger_price"))
            current_limit = str(current_config.get("limit_price"))

            requested_stop = str(data["stop_price"])
            requested_limit = str(data["take_profit_price"])

            if current_stop == requested_stop and current_limit == requested_limit:
                return {
                    "status": "ignored",
                    "reason": "Protection déjà synchronisée.",
                    "protection": protection,
                }

            self.exchange.cancel_protection_order()

        client_order_id = f"{data.get('strategy', 'strategy')}-protection-{uuid.uuid4()}"

        side = "SELL" if position["side"] == "LONG" else "BUY"

        result = self.exchange.create_protection_order(
            side=side,
            contracts=position["contracts"],
            stop_trigger_price=data["stop_price"],
            limit_price=data["take_profit_price"],
            client_order_id=client_order_id,
        )

        return {
            "status": "updated",
            "result": result,
        }
