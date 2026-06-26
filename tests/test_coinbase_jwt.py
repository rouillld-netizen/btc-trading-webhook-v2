from coinbase import jwt_generator
from config import COINBASE_API_KEY, COINBASE_API_SECRET

print("KEY:", COINBASE_API_KEY[:25])
print("FIRST:", COINBASE_API_SECRET.splitlines()[0])
print("LAST:", COINBASE_API_SECRET.splitlines()[-1])

jwt = jwt_generator.build_rest_jwt(
    "GET /api/v3/brokerage/accounts",
    COINBASE_API_KEY,
    COINBASE_API_SECRET,
)

print("JWT OK")
print(jwt[:50])
