import os
import time
import hmac
import hashlib
from decimal import Decimal
from urllib.parse import urlencode
from datetime import datetime, timezone

import requests
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

APP_VERSION = "2026-06-20-v17"

PROCESSED_EVENTS = set()

OPEN_POSITIONS = {}

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "test-secret")

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BINANCE_BASE_URL = "https://api.binance.com"

# Binance : arrondi d'une quantité au stepSize autorisé
def round_step_size(quantity, step_size):
    quantity = Decimal(str(quantity))
    step_size = Decimal(str(step_size))
    return str((quantity // step_size) * step_size)

@app.get("/")
def home():
    return {
        "status": "online",
        "version": APP_VERSION
    }

@app.get("/ip")
def get_ip():
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=10)
        return {"status": "ok", "ip_info": r.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/binance/ping")
def binance_ping():
    try:
        r = requests.get(f"{BINANCE_BASE_URL}/api/v3/ping", timeout=10)
        return {"status_code": r.status_code, "response": r.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/binance/time")
def binance_time():
    try:
        r = requests.get(f"{BINANCE_BASE_URL}/api/v3/time", timeout=10)
        return {"status_code": r.status_code, "response": r.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


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


def binance_signed_post(path, params=None):
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

    response = requests.post(
        url,
        headers={"X-MBX-APIKEY": BINANCE_API_KEY},
        timeout=10,
    )

    if response.status_code != 200:
        print("BINANCE_POST_ERROR:", response.status_code, response.text)
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()

def get_margin_usdc_available():
    data = binance_signed_get("/sapi/v1/margin/account")
    assets = data.get("userAssets", [])

    for asset in assets:
        if asset.get("asset") == "USDC":
            return float(asset.get("netAsset", 0))

    return 0.0


def calculate_position_size(
    capital_available,
    capital_pct,
    risk_pct,
    max_leverage,
    entry_price,
    sl_price
):
    capital_max = capital_available * (capital_pct / 100)
    risk_max = capital_available * (risk_pct / 100)
    risk_per_btc = abs(entry_price - sl_price)

    if risk_per_btc <= 0:
        return {
            "status": "error",
            "reason": "invalid stop distance",
        }

    qty_risk = risk_max / risk_per_btc
    qty_leverage = (capital_max * max_leverage) / entry_price
    qty_final = min(qty_risk, qty_leverage)

    return {
        "capital_available": capital_available,
        "capital_max": capital_max,
        "risk_max": risk_max,
        "risk_per_btc": risk_per_btc,
        "qty_risk": qty_risk,
        "qty_leverage": qty_leverage,
        "qty_final": qty_final,
        "position_value": qty_final * entry_price,
    }

def build_order_plan(data, position_calc):
    mode = str(data.get("mode", "")).lower()

    if mode == "test":
        test_usdc = float(data.get("test_usdc", 0))

        if test_usdc <= 0:
            return {
                "status": "error",
                "reason": "invalid test_usdc"
            }

        return {
            "mode": "test",
            "quote_order_qty": test_usdc,
            "position_calc_used": False
        }

    if mode == "live":
        if not position_calc:
            return {
                "status": "error",
                "reason": "missing position_calc"
            }

        return {
            "mode": "live",
            "quantity": position_calc["qty_final"],
            "position_value": position_calc["position_value"],
            "position_calc_used": True
        }

    return {
        "status": "ignored",
        "reason": "mode not executable"
    }

def place_long_stop_loss(quantity, sl_price):
    btc_qty = round_step_size(quantity, "0.00001")

    stop_price = round(float(sl_price), 2)
    limit_price = round(float(sl_price) * 0.999, 2)

    print("LONG_STOP_QTY:", btc_qty)
    print("LONG_STOP_PRICE:", stop_price)
    print("LONG_STOP_LIMIT:", limit_price)

    if float(btc_qty) <= 0:
        return {
            "status": "ignored",
            "reason": "stop quantity too small",
            "btc_qty": btc_qty,
        }

    return binance_signed_post(
        "/sapi/v1/margin/order",
        {
            "symbol": "BTCUSDC",
            "side": "SELL",
            "type": "STOP_LOSS_LIMIT",
            "quantity": btc_qty,
            "stopPrice": str(stop_price),
            "price": str(limit_price),
            "timeInForce": "GTC",
            "sideEffectType": "NO_SIDE_EFFECT",
        },
    )

def execute_test_long_order(action, order_plan, data):
    if not order_plan or order_plan.get("mode") != "test":
        return None

    if action == "open_long":
        result = binance_signed_post(
            "/sapi/v1/margin/order",
            {
                "symbol": "BTCUSDC",
                "side": "BUY",
                "type": "MARKET",
                "quoteOrderQty": str(order_plan["quote_order_qty"]),
                "sideEffectType": "NO_SIDE_EFFECT",
            },
        )

        executed_qty = float(result.get("executedQty", 0))

        key = "BTC_H1_LONG"
        OPEN_POSITIONS[key] = OPEN_POSITIONS.get(key, 0.0) + executed_qty

        print("OPEN_POSITION_UPDATED:", key, OPEN_POSITIONS[key])

        stop_result = place_long_stop_loss(
            quantity=executed_qty,
            sl_price=data.get("sl_price"),
        )

        print("LONG_STOP_RESULT:", stop_result)

        return {
            "entry_order": result,
            "stop_order": stop_result,
        }

        key = "BTC_H1_LONG"
        OPEN_POSITIONS[key] = OPEN_POSITIONS.get(key, 0.0) + executed_qty

        print("OPEN_POSITION_UPDATED:", key, OPEN_POSITIONS[key])

        return result
    
    if action == "close_long":
        key = "BTC_H1_LONG"
        btc_tracked = OPEN_POSITIONS.get(key, 0.0)

        print("BTC_TRACKED:", btc_tracked)

        if btc_tracked <= 0:
            return {
                "status": "ignored",
                "reason": "no tracked BTC position to close",
            }

        btc_qty = round_step_size(btc_tracked, "0.00001")

        print("BTC_QTY:", btc_qty)

        if float(btc_qty) <= 0:
            return {
                "status": "ignored",
                "reason": "BTC quantity too small after LOT_SIZE rounding",
                "btc_tracked": btc_tracked,
                "btc_qty": btc_qty,
            }

        result = binance_signed_post(
            "/sapi/v1/margin/order",
            {
                "symbol": "BTCUSDC",
                "side": "SELL",
                "type": "MARKET",
                "quantity": btc_qty,
                "sideEffectType": "NO_SIDE_EFFECT",
            },
        )

        OPEN_POSITIONS[key] = 0.0

        print("OPEN_POSITION_CLOSED:", key)

        return result

    return None

@app.get("/binance/spot-account")
def binance_spot_account():
    data = binance_signed_get("/api/v3/account", {"omitZeroBalances": "true"})

    return {
        "status": "ok",
        "account_type": "spot",
        "can_trade": data.get("canTrade"),
        "balances": data.get("balances", []),
    }

def execute_test_short_order(action, order_plan):
    if not order_plan or order_plan.get("mode") != "test":
        return None

    if action == "open_short":
        result = binance_signed_post(
            "/sapi/v1/margin/order",
            {
                "symbol": "BTCUSDC",
                "side": "SELL",
                "type": "MARKET",
                "quoteOrderQty": str(order_plan["quote_order_qty"]),
                "sideEffectType": "AUTO_BORROW_REPAY",
            },
        )

        executed_qty = float(result.get("executedQty", 0))

        key = "BTC_H1_SHORT"
        OPEN_POSITIONS[key] = OPEN_POSITIONS.get(key, 0.0) + executed_qty

        print("SHORT_POSITION_UPDATED:", key, OPEN_POSITIONS[key])

        return result

    if action == "close_short":
        key = "BTC_H1_SHORT"
        btc_tracked = OPEN_POSITIONS.get(key, 0.0)

        print("SHORT_BTC_TRACKED:", btc_tracked)

        if btc_tracked <= 0:
            return {
                "status": "ignored",
                "reason": "no tracked BTC short position to close",
            }

        btc_qty = round_step_size(btc_tracked, "0.00001")

        print("SHORT_BTC_QTY:", btc_qty)

        if float(btc_qty) <= 0:
            return {
                "status": "ignored",
                "reason": "BTC short quantity too small after LOT_SIZE rounding",
                "btc_tracked": btc_tracked,
                "btc_qty": btc_qty,
            }

        result = binance_signed_post(
            "/sapi/v1/margin/order",
            {
                "symbol": "BTCUSDC",
                "side": "BUY",
                "type": "MARKET",
                "quantity": btc_qty,
                "sideEffectType": "AUTO_REPAY",
            },
        )

        OPEN_POSITIONS[key] = 0.0

        print("SHORT_POSITION_CLOSED:", key)

        return result

    return None

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


@app.get("/binance/order-test")
def binance_order_test():
    return binance_signed_post(
        "/api/v3/order/test",
        {
            "symbol": "BTCUSDC",
            "side": "BUY",
            "type": "MARKET",
            "quoteOrderQty": "10",
        },
    )


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

    event_id = data.get("event_id")

    if event_id:
        if event_id in PROCESSED_EVENTS:
            print("DUPLICATE_EVENT_IGNORED:", event_id)
            return {
                "ok": True,
                "message": "Duplicate event ignored",
                "event_id": event_id,
            }

        PROCESSED_EVENTS.add(event_id)

    print("WEBHOOK_RECEIVED:", safe_data)

    binance_result = None
    position_calc = None
    order_plan = None

    if data.get("action") in ["open_long", "open_short"]:
        position_calc = calculate_position_size(
            capital_available=get_margin_usdc_available(),
            capital_pct=float(data.get("capital_pct", 0)),
            risk_pct=float(data.get("risk_pct", 0)),
            max_leverage=float(data.get("max_leverage", 1)),
            entry_price=float(data.get("entry_price", 0)),
            sl_price=float(data.get("sl_price", 0)),
        )

        print("POSITION_CALC:", position_calc)

        order_plan = build_order_plan(data, position_calc)
        print("ORDER_PLAN:", order_plan)

    action = data.get("action")

    if action in ["open_long", "close_long", "open_short", "close_short"]:
        if data.get("mode") == "Test":
            test_plan = {
                "mode": "test",
                "quote_order_qty": float(data.get("test_usdc", 0)),
                "position_calc_used": False,
            }

            if action in ["open_long", "close_long"]:
                binance_result = execute_test_long_order(action, test_plan, data)

            if action in ["open_short", "close_short"]:
                binance_result = execute_test_short_order(action, test_plan)

            print("BINANCE_RESULT:", binance_result)

    should_notify = data.get("notify", True)
    if should_notify:
        send_push(
            f"🚀 {data.get('action', 'unknown')}\n"
            f"Mode : {data.get('mode', '-')}\n"
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
        "mode": data.get("mode"),
        "notify": should_notify,
    }

    return {
        "ok": True,
        "message": "Signal received",
        "data": log,
        "binance_result": binance_result,
        "position_calc": position_calc,
        "order_plan": order_plan,
    }