# Lyftr AI – Backend Assignment by Divyansh Sethi

FastAPI-based webhook ingestion service with idempotency, analytics, and observability.

important---- The service requires WEBHOOK_SECRET and DATABASE_URL to be set as environment variables, as per the assignment instructions

## Setup Used
VSCode + Python venv

## Requirements
- Docker
- Docker Compose

## How to Run

```bash
export WEBHOOK_SECRET="testsecret"
make up

Service will be available at:
http://localhost:8000

Health Checks
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

Webhook
Endpoint

POST /webhook

## Signature:

hex(HMAC_SHA256(secret=WEBHOOK_SECRET, message=raw_request_body))


Idempotency enforced via message_id primary key.

##Messages

GET /messages

Supports:

pagination (limit, offset)

filter by sender (from_msisdn)

filter by timestamp (since)

free-text search (q)

Ordering: ts ASC, message_id ASC

##Stats

GET /stats

Returns:

total messages

unique senders

top senders

first and last message timestamps

## Metrics

GET /metrics

Exposes Prometheus-style metrics including:

http_requests_total

webhook_requests_total

request latency histogram

Design Decisions:- 

-SQLite used with volume-backed persistence
-Raw-body HMAC verification for webhook authenticity
-Graceful idempotency using DB constraints
-Metrics and logs emitted to stdout for container observability
