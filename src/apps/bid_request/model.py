from decimal import Decimal
from pydantic import BaseModel, Field


class CreateBidRequestModel(BaseModel):
    floor_price: Decimal
    timeout:int
    session_id:str
    user_id:str
    request_id:str


class BidderResponseModel(BaseModel):
    name:str
    price:Decimal


class BidWinnerModel(BidderResponseModel):
    pass


class RetrieveBidResultModel(BaseModel):
    session_id:str
    request_id:str
    win_bid:BidWinnerModel=Field(default_factory={})
    bid_responses:list[BidderResponseModel]
    
    
