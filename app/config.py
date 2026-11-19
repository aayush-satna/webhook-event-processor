import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "dev_secret_key_change_in_prod")
IDEMPOTENCY_TTL_SECONDS = int(os.getenv("IDEMPOTENCY_TTL_SECONDS", "86400"))
