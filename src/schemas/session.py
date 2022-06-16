from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from core.enums import SessionStatusEnum


class BidderSchema(BaseModel):
    name: str
    endpoint: str
    session_status: Optional[SessionStatusEnum]


class SessionSchema(BaseModel):
    session_id: str
    status: SessionStatusEnum
    estimated_traffic: int
    bidders: list[dict[str, BidderSchema]]
    budget: Decimal
    impression_goal: int
