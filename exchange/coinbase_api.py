import requests
from coinbase import jwt_generator

BASE_URL = "https://api.coinbase.com"


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
