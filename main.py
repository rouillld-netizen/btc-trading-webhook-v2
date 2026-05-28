import os
from datetime import datetime, timezone

from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "test-secret")


@app.get("/")
def home():
    return {"status": "online"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    if data.get("secret") != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret")

    log = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "symbol": data.get("symbol"),
        "action": data.get("action"),
        "tf": data.get("tf"),
        "price": data.get("price"),
        "time": data.get("time"),
    }

    print("WEBHOOK_RECEIVED:", log)

    return {
        "ok": True,
        "message": "Signal received",
        "data": log,
    }
