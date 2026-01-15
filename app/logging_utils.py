import json
import logging
import sys
from datetime import datetime
from uuid import uuid4


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "request_id": getattr(record, "request_id", None),
            "method": getattr(record, "method", None),
            "path": getattr(record, "path", None),
            "status": getattr(record, "status", None),
            "latency_ms": getattr(record, "latency_ms", None),
        }

        return json.dumps({k: v for k, v in payload.items() if v is not None})


def setup_logger(level: str):
    logging.basicConfig(
        level=level,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    logger = logging.getLogger("lyftr")
    logger.setLevel(level)
    logger.propagate = False

    for h in logger.handlers:
        h.setFormatter(JsonFormatter())

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger


def new_request_id():
    return str(uuid4())
