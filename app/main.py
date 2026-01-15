import time
from fastapi import FastAPI, Request, Response, status
from app.models import init_db
from app.config import settings
from app.logging_utils import setup_logger, new_request_id
import hmac
import hashlib
from fastapi import HTTPException
from app.schemas import WebhookMessage
from app.storage import insert_message
from app.storage import list_messages
from app.storage import get_stats
from app.metrics import (
    http_requests_total,
    webhook_requests_total,
    request_latency_ms,
)
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

logger = setup_logger(settings.log_level)

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    latency_ms = int((time.time() - start) * 1000)

    http_requests_total.labels(
        path=request.url.path,
        status=str(response.status_code),
    ).inc()

    request_latency_ms.observe(latency_ms)

    return response

@app.get("/health/live")
def health_live():
    return {"status": "live"}


@app.get("/health/ready")
def health_ready(response: Response):
    try:
        init_db()
        _ = settings.webhook_secret
        return {"status": "ready"}
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not ready"}

@app.post("/webhook")
async def webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("X-Signature")

    if not signature:
        webhook_requests_total.labels(result="invalid_signature").inc()
        raise HTTPException(status_code=401, detail="invalid signature")

    expected = hmac.new(
        settings.webhook_secret.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        webhook_requests_total.labels(result="invalid_signature").inc()
        raise HTTPException(status_code=401, detail="invalid signature")

    try:
        payload = WebhookMessage.model_validate_json(raw_body)
    except Exception:
        webhook_requests_total.labels(result="validation_error").inc()
        raise HTTPException(status_code=422)

    result = insert_message(payload)

    webhook_requests_total.labels(result=result).inc()

    return {"status": "ok"}

@app.get("/messages")
def get_messages(
    limit: int = 50,
    offset: int = 0,
    from_msisdn: str | None = None,
    since: str | None = None,
    q: str | None = None,
):
    if limit < 1 or limit > 100 or offset < 0:
        raise HTTPException(status_code=422)

    data, total = list_messages(
        limit=limit,
        offset=offset,
        from_msisdn=from_msisdn,
        since=since,
        q=q,
    )

    return {
        "data": data,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

@app.get("/stats")
def stats():
    return get_stats()
    data = get_stats()
    return data

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
