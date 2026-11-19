# Idempotent Webhook Event Processor

Production-style FastAPI + Redis webhook ingestion gateway featuring HMAC-SHA256 payload authentication, atomic `SET NX` deduplication, TTL state retention, and Docker Compose orchestration.

### Architecture
- `app/security.py` — Constant-time `hmac.compare_digest` signature verification against `X-Signature-256`.
- `app/store.py` — Atomic Redis `SET NX EX` idempotency guard preventing duplicate event processing on provider retries.
- `app/main.py` — `/health` Redis probe, `/api/v1/webhooks/ingest` endpoint, and `/api/v1/webhooks/{event_id}` audit lookup.

### Run Locally
    docker compose up --build
