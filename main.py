import os
import requests
from datetime import datetime, timezone

from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "test-secret")


@app.get("/")
def home():
    return {"status": "online"}


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


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    # Vérification du secret
    if data.get("secret") != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret")

    # Log complet Railway
    print("WEBHOOK_RECEIVED:", data)

    # Notification téléphone
    send_push(
        f"🚀 {data.get('action', 'unknown')}\n"
        f"Symbole : {data.get('symbol', '-')}\n"
        f"Stratégie : {data.get('strategy', '-')}"
    )

    log = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "action": data.get("action"),
        "symbol": data.get("symbol"),
        "strategy": data.get("strategy"),
    }

    return {
        "ok": True,
        "message": "Signal received",
        "data": log,
    }