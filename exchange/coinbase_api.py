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
