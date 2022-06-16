import decimal
from decimal import Decimal

from pydantic import BaseModel, Field

decimal.Context(prec=2)


class CreateBidRequestModel(BaseModel):
    floor_price: Decimal = Field(gt=0)
    timeout_ms: int
    session_id: str
    user_id: str
    request_id: str


class BidderResponseModel(BaseModel):
    name: str
    price: Decimal


class RetrieveBidResultModel(BaseModel):
    session_id: str
    request_id: str
    win_bid: BidderResponseModel = Field(default_factory={})
    bid_responses: list[BidderResponseModel]
