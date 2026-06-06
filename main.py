import os
import time
import hmac
import hashlib
from urllib.parse import urlencode
from datetime import datetime, timezone

import requests
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "test-secret")

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BINANCE_BASE_URL = "https://api.binance.com"


@app.get("/")
def home():
    return {"status": "online"}

@app.get("/ip")
def get_ip():
    try:
        r = requests.get(
            "https://api.ipify.org?format=json",
            timeout=10
        )

        return {
            "status": "ok",
            "ip_info": r.json()
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/binance/ping")
def binance_ping():
    try:
        r = requests.get(
            "https://api.binance.com/api/v3/ping",
            timeout=10
        )

        return {
            "status_code": r.status_code,
            "response": r.text
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/binance/time")
def binance_time():
    try:
        r = requests.get(
            "https://api.binance.com/api/v3/time",
            timeout=10
        )

        return {
            "status_code": r.status_code,
            "response": r.text
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/binance/server-time")
def binance_server_time():
    r = requests.get(
        "https://api.binance.com/api/v3/time",
        timeout=10
    )
    return r.json()

@app.get("/binance/key-test")
def binance_key_test():

    r = requests.get(
        "https://api.binance.com/api/v3/account",
        headers={
            "X-MBX-APIKEY": BINANCE_API_KEY
        },
        timeout=10
    )

    return {
        "status_code": r.status_code,
        "response": r.text
    }

def send_push(message):
    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.getenv("PUSHOVER_API_TOKEN"),
                "user": os.getenv("PUSHOVER_USER_KEY"),
                "message": message,
            },
            timeout=10,
        )
    except Exception as e:
        print(f"PUSHOVER_ERROR: {e}")


def binance_signed_get(path, params=None):
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        raise HTTPException(status_code=500, detail="Binance API variables missing")

    params = params or {}
    params["timestamp"] = int(time.time() * 1000)
    params["recvWindow"] = 5000

    query_string = urlencode(params)
    signature = hmac.new(
        BINANCE_API_SECRET.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    url = f"{BINANCE_BASE_URL}{path}?{query_string}&signature={signature}"

    response = requests.get(
        url,
        headers={"X-MBX-APIKEY": BINANCE_API_KEY},
        timeout=10,
    )

    if response.status_code != 200:
        print("BINANCE_ERROR:", response.status_code, response.text)
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()


@app.get("/binance/spot-account")
def binance_spot_account():
    data = binance_signed_get("/api/v3/account", {"omitZeroBalances": "true"})

    balances = data.get("balances", [])

    return {
        "status": "ok",
        "account_type": "spot",
        "can_trade": data.get("canTrade"),
        "balances": balances,
    }


@app.get("/binance/margin-account")
def binance_margin_account():
    data = binance_signed_get("/sapi/v1/margin/account")

    assets = data.get("userAssets", [])

    filtered_assets = [
        {
            "asset": a.get("asset"),
            "free": a.get("free"),
            "locked": a.get("locked"),
            "borrowed": a.get("borrowed"),
            "interest": a.get("interest"),
            "netAsset": a.get("netAsset"),
        }
        for a in assets
        if a.get("asset") in ["BTC", "USDC", "USDT"]
    ]

    return {
        "status": "ok",
        "account_type": "cross_margin",
        "margin_level": data.get("marginLevel"),
        "total_asset_of_btc": data.get("totalAssetOfBtc"),
        "total_liability_of_btc": data.get("totalLiabilityOfBtc"),
        "total_net_asset_of_btc": data.get("totalNetAssetOfBtc"),
        "assets": filtered_assets,
    }


@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if data.get("secret") != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret")

    safe_data = data.copy()
    safe_data.pop("secret", None)

    print("WEBHOOK_RECEIVED:", safe_data)

    should_notify = data.get("notify", True)

    if should_notify:
        send_push(
            f"🚀 {data.get('action', 'unknown')}\n"
            f"Symbole : {data.get('symbol', '-')}\n"
            f"Stratégie : {data.get('strategy', '-')}\n"
            f"Entrée : {data.get('entry_price', '-')}\n"
            f"SL : {data.get('sl_price', '-')}\n"
            f"TP : {data.get('tp_price', '-')}"
        )

    log = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "action": data.get("action"),
        "symbol": data.get("symbol"),
        "strategy": data.get("strategy"),
        "notify": should_notify,
    }

    return {
        "ok": True,
        "message": "Signal received",
        "data": log,
    }