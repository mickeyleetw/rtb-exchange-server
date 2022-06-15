from decimal import Decimal

from pydantic import BaseModel

from core.enums import ResultEnum, SessionStatusEnum


class BidderModel(BaseModel):
    name: str
    endpoint: str


class BidderRequirementModel(BaseModel):
    budget: Decimal
    impression_goal: int


class InitBidderSessionModel(BaseModel):
    session_id: str
    estimated_traffic: int
    budget: Decimal
    impression_goal: int


class EndBidderSessionModel(BaseModel):
    session_id: str


class BidderSessionResponseModel(BaseModel):
    session_id: str
    status: SessionStatusEnum
    exchange_session_id: str
    result: ResultEnum
