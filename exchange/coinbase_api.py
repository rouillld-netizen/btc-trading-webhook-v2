import requests
from coinbase import jwt_generator

BASE_URL = "https://api.coinbase.com"
FCM_BTC_PERP = "BIP-20DEC30-CDE"

class CoinbaseAPI:

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
