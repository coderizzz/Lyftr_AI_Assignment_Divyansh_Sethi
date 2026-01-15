from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class WebhookMessage(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_msisdn: str = Field(..., alias="from")
    to_msisdn: str = Field(..., alias="to")
    ts: datetime
    text: Optional[str] = Field(None, max_length=4096)

    @field_validator("from_msisdn", "to_msisdn")
    @classmethod
    def validate_msisdn(cls, v):
        if not re.fullmatch(r"\+[0-9]+", v):
            raise ValueError("invalid msisdn")
        return v
