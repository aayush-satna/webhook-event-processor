import json
import redis
from app.config import IDEMPOTENCY_TTL_SECONDS, REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def claim_event(event_id: str, payload: dict) -> bool:
    """Atomically sets the event key in Redis only if it does not already exist."""
    key = f"webhook:event:{event_id}"
    was_set = redis_client.set(
        key,
        json.dumps({"status": "processed", "payload": payload}),
        nx=True,
        ex=IDEMPOTENCY_TTL_SECONDS,
    )
    return bool(was_set)


def get_event(event_id: str) -> dict | None:
    raw = redis_client.get(f"webhook:event:{event_id}")
    return json.loads(raw) if raw else None
