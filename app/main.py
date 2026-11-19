import hashlib
import json
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Header, HTTPException, Request

from app.config import WEBHOOK_SECRET
from app.security import verify_hmac_signature
from app.store import claim_event, get_event, redis_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
app = FastAPI(title="Idempotent Webhook Event Processor", version="1.0.0")


@app.get("/health")
def health_check():
    try:
        redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Redis unavailable: {exc}")


@app.post("/api/v1/webhooks/ingest")
async def ingest_webhook(
    request: Request,
    x_event_id: str | None = Header(default=None),
    x_signature_256: str | None = Header(default=None),
):
    raw_body = await request.body()
    if not raw_body:
        raise HTTPException(status_code=400, detail="Empty request body")

    verify_hmac_signature(raw_body, x_signature_256, WEBHOOK_SECRET)

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Malformed JSON payload")

    event_id = x_event_id or hashlib.sha256(raw_body).hexdigest()
    is_new = claim_event(event_id, payload)

    if not is_new:
        logging.info(f"Duplicate webhook skipped: {event_id}")
        return {"status": "duplicate_ignored", "event_id": event_id}

    logging.info(f"Processed webhook {event_id} at {datetime.now(timezone.utc).isoformat()}")
    return {"status": "processed", "event_id": event_id}


@app.get("/api/v1/webhooks/{event_id}")
def fetch_event_status(event_id: str):
    record = get_event(event_id)
    if not record:
        raise HTTPException(status_code=404, detail="Event not found or expired")
    return {"event_id": event_id, **record}
