from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class BidderSchema(BaseModel):
    name: str
    url: str
    price: Decimal


class BidRequestSchema(BaseModel):
    request_id: str
    session_id: str
    user_id: str
    floor_price: Decimal
    timeout: int
    win_bid: Optional[BidderSchema]
    bid_responses: list[BidderSchema]
