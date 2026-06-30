import requests
from coinbase import jwt_generator
from exchange.base import ExchangeAdapter

BASE_URL = "https://api.coinbase.com"
FCM_BTC_PERP = "BIP-20DEC30-CDE"

class CoinbaseAPI(ExchangeAdapter):

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret


    def _jwt(self, method, path):
        uri = jwt_generator.format_jwt_uri(method, path)
        return jwt_generator.build_rest_jwt(
            uri,
            self.api_key,
            self.api_secret,
        )


    def get_accounts(self):

        path = "/api/v3/brokerage/accounts"

        token = self._jwt("GET", path)

        headers = {
            "Authorization": f"Bearer {token}"
        }

        r = requests.get(
            BASE_URL + path,
            headers=headers,
            timeout=30
        )

        r.raise_for_status()

        return r.json()

    def get_products(self, params=None):

        path = "/api/v3/brokerage/products"

        token = self._jwt("GET", path)

        headers = {
            "Authorization": f"Bearer {token}"
        }

        r = requests.get(
            BASE_URL + path,
            headers=headers,
            params=params or {},
            timeout=30
        )

        r.raise_for_status()

        return r.json()

    def get_product(self, product_id):

        path = f"/api/v3/brokerage/products/{product_id}"

        token = self._jwt("GET", path)

        headers = {
            "Authorization": f"Bearer {token}"
        }

        r = requests.get(
            BASE_URL + path,
            headers=headers,
            timeout=30
        )

        r.raise_for_status()

        return r.json()

    def get_positions(self):

        path = "/api/v3/brokerage/cfm/positions"

        token = self._jwt("GET", path)

        headers = {
            "Authorization": f"Bearer {token}"
        }

        r = requests.get(
            BASE_URL + path,
            headers=headers,
            timeout=30
        )

        r.raise_for_status()

        return r.json()

    def get_orders(self):

        path = "/api/v3/brokerage/orders/historical/batch"

        token = self._jwt("GET", path)

        headers = {
            "Authorization": f"Bearer {token}"
        }

        r = requests.get(
            BASE_URL + path,
            headers=headers,
            timeout=30
        )

        r.raise_for_status()

        return r.json()

    def create_order(self, payload):

        path = "/api/v3/brokerage/orders"

        token = self._jwt("POST", path)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        r = requests.post(
            BASE_URL + path,
            headers=headers,
            json=payload,
            timeout=30
        )

        if not r.ok:
            print("STATUS:", r.status_code)
            print("BODY:", r.text)

        r.raise_for_status()

        return r.json()

    def preview_order(self, payload):

        path = "/api/v3/brokerage/orders/preview"

        token = self._jwt("POST", path)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        r = requests.post(
            BASE_URL + path,
            headers=headers,
            json=payload,
            timeout=30
        )

        if not r.ok:
            print("STATUS:", r.status_code)
            print("BODY:", r.text)

        r.raise_for_status()

        return r.json()

    def open_long_with_stop(self, contracts, stop_trigger_price, limit_price, client_order_id):

        payload = {
            "client_order_id": client_order_id,
            "product_id": FCM_BTC_PERP,
            "side": "BUY",
            "order_configuration": {
                "marketMarketIoc": {
                    "baseSize": str(contracts)
                }
            },
            "attached_order_configuration": {
                "triggerBracketGtc": {
                    "stopTriggerPrice": str(stop_trigger_price),
                    "limitPrice": str(limit_price)
                }
            }
        }

        return self.create_order(payload)

    def create_market_order(self, side, contracts, client_order_id, stop_trigger_price=None, limit_price=None):

        payload = {
            "client_order_id": client_order_id,
            "product_id": FCM_BTC_PERP,
            "side": side,
            "order_configuration": {
                "marketMarketIoc": {
                    "baseSize": str(contracts)
                }
            }
        }

        if stop_trigger_price is not None and limit_price is not None:
            payload["attached_order_configuration"] = {
                "triggerBracketGtc": {
                    "stopTriggerPrice": str(stop_trigger_price),
                    "limitPrice": str(limit_price)
                }
            }

        return self.create_order(payload)

    def get_position(self):

        positions = self.get_positions().get("positions", [])

        for position in positions:
            if position.get("product_id") == FCM_BTC_PERP:
                return {
                    "product_id": position.get("product_id"),
                    "side": position.get("side"),
                    "contracts": position.get("number_of_contracts"),
                    "entry_price": position.get("avg_entry_price"),
                    "current_price": position.get("current_price"),
                    "unrealized_pnl": position.get("unrealized_pnl"),
                }

        return None

    def get_open_orders(self):

        orders = self.get_orders().get("orders", [])

        result = []

        for order in orders:
            if (
                order.get("product_id") == FCM_BTC_PERP
                and order.get("status") == "OPEN"
            ):
                result.append({
                    "order_id": order.get("order_id"),
                    "client_order_id": order.get("client_order_id"),
                    "side": order.get("side"),
                    "order_type": order.get("order_type"),
                    "status": order.get("status"),
                    "configuration": order.get("order_configuration"),
                    "originating_order_id": order.get("originating_order_id"),
                })

        return result

    def get_balance(self, currency="USDC"):

        accounts = self.get_accounts().get("accounts", [])

        for account in accounts:
            if account.get("currency") == currency:
                return {
                    "currency": currency,
                    "available": account.get("available_balance", {}).get("value"),
                    "hold": account.get("hold", {}).get("value"),
                }

        return None

    def cancel_order(self, order_id):

        path = "/api/v3/brokerage/orders/batch_cancel"

        token = self._jwt("POST", path)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "order_ids": [order_id]
        }

        r = requests.post(
            BASE_URL + path,
            headers=headers,
            json=payload,
            timeout=30
        )

        if not r.ok:
            print("STATUS:", r.status_code)
            print("BODY:", r.text)

        r.raise_for_status()

        return r.json()

    def close_long(self):

        open_orders = self.get_open_orders()

        for order in open_orders:
            self.cancel_order(order["order_id"])

        position = self.get_position()

        if position is None:
            return {
                "success": False,
                "message": "Aucune position ouverte."
            }

        return self.create_market_order(
            side="SELL",
            contracts=position["contracts"],
            client_order_id="close-long",
        )

    def get_protection_order(self):

        open_orders = self.get_open_orders()

        for order in open_orders:
            if order.get("order_type") == "TAKE_PROFIT_STOP_LOSS":
                return order

        return None

    def cancel_protection_order(self):

        protection_order = self.get_protection_order()

        if protection_order is None:
            return {
                "success": False,
                "message": "Aucun ordre de protection ouvert."
            }

        return self.cancel_order(protection_order["order_id"])
