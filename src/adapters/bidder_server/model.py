from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from core.enums import ResultEnum, SessionStatusEnum


class BidderSessionModel:

    class InitSessionModel(BaseModel):
        session_id: str
        estimated_traffic: int
        budget: Decimal
        impression_goal: int

    class EndSessionModel(BaseModel):
        session_id: str

    class SessionResponseModel(BaseModel):
        status: SessionStatusEnum
        exchange_session_id: str
        result: Optional[ResultEnum]


class BidderBidRequestModel:

    class CreateBidRequestModel(BaseModel):
        floor_price: Decimal
        timeout_ms: int
        session_id: str
        user_id: str
        request_id: str

    class RetrieveBidResultModel(BaseModel):
        session_id: str
        request_id: str
        price: Decimal

    class BidResultNotificationModel(BaseModel):
        session_id: str
        request_id: str
        clear_price: Decimal

    class NotificationResponse(BaseModel):
        result: ResultEnum
