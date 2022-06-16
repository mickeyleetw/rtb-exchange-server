import decimal
from decimal import Decimal

from pydantic import BaseModel, Field

from core.enums import ResultEnum, SessionStatusEnum

decimal.Context(prec=2)


class BidderModel(BaseModel):
    name: str
    endpoint: str


class BidderRequirementModel(BaseModel):
    budget: Decimal = Field(gt=0)
    impression_goal: int = Field(gt=0)


class InitSessionModel(BaseModel):
    session_id: str
    estimated_traffic: int = Field(gt=0)
    bidders: list[BidderModel]
    bidder_setting: BidderRequirementModel


class EndSessionModel(BaseModel):
    session_id: str


class SessionResponseModel(BaseModel):
    session_id: str
    status: SessionStatusEnum
    estimated_traffic: int
    bidders: list[BidderModel]
    result: ResultEnum
