import functools
import os
from json import JSONDecodeError
from typing import Callable

import requests
from fastapi import status
from fastapi.encoders import jsonable_encoder
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from adapters.bidder_server.model import BidderBidRequestModel, BidderSessionModel
from core.enums import ErrorCode
from core.exception import BidderServiceException

MOUNT_PREFIX = os.getenv('MOUNT_PREFIX', 'http://')
RTB_BIDDER_API_RETIRES = 1


def http_error_handler(func: Callable):

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            return BidderServiceException(code=ErrorCode.BIDDER_API_2002_CONNECTION_ERROR, msg=str(e))
        except requests.exceptions.Timeout:
            msg = 'request time out'
            return BidderServiceException(code=ErrorCode.BIDDER_API_2003_REQUEST_TIME_OUT, msg=msg)
        except requests.exceptions.HTTPError as e:
            try:
                data = e.response.json(strict=False)
                msg = f"{data['code']}, {data['message']}"
            except (JSONDecodeError, KeyError):
                msg = e.response.text
            return BidderServiceException(msg)

    return wrapper


class BidderServiceAdapter:

    @staticmethod
    def get_request_session():
        retries = Retry(
            total=RTB_BIDDER_API_RETIRES,
            backoff_factor=2,
            allowed_methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'],
            status_forcelist=[
                status.HTTP_429_TOO_MANY_REQUESTS,
                status.HTTP_502_BAD_GATEWAY,
                status.HTTP_503_SERVICE_UNAVAILABLE,
                status.HTTP_504_GATEWAY_TIMEOUT,
            ]
        )
        session = requests.Session()
        session.mount(MOUNT_PREFIX, HTTPAdapter(max_retries=retries))

        return session


class BidderSessionAdapter(BidderServiceAdapter):

    @classmethod
    @http_error_handler
    async def init_bidder_session(
        cls, rtb_bidder_api_url: str, bidder_session: BidderSessionModel.InitSessionModel
    ) -> BidderSessionModel.SessionResponseModel:
        session = cls.get_request_session()
        resp = session.post(f'{rtb_bidder_api_url}/sessions/init', json=jsonable_encoder(bidder_session))
        resp.raise_for_status()
        bidder_session_response = BidderSessionModel.SessionResponseModel(**(resp.json()))
        return bidder_session_response

    @classmethod
    @http_error_handler
    async def end_bidder_session(
        cls, rtb_bidder_api_url: str, data: BidderSessionModel.EndSessionModel
    ) -> BidderSessionModel.SessionResponseModel:
        session = cls.get_request_session()
        resp = session.post(f'{rtb_bidder_api_url}/sessions/end', json=jsonable_encoder(data))
        resp.raise_for_status()
        bidder_session_response = BidderSessionModel.SessionResponseModel(**(resp.json()))
        return bidder_session_response


class BidderBidRequestAdapter(BidderServiceAdapter):

    @classmethod
    @http_error_handler
    async def bidder_create_bid_request(
        cls, rtb_bidder_api_url: str, bidder_bid_request: BidderBidRequestModel.CreateBidRequestModel, time_out: int
    ) -> BidderBidRequestModel.RetrieveBidResultModel:
        session = requests.Session()
        resp = session.post(
            f'{rtb_bidder_api_url}/bid-requests', json=jsonable_encoder(bidder_bid_request), timeout=time_out
        )
        resp.raise_for_status()
        bidder_bid_result = BidderBidRequestModel.RetrieveBidResultModel(**(resp.json()))
        return bidder_bid_result

    @classmethod
    @http_error_handler
    async def result_notified(
        cls, rtb_bidder_api_url: str, result_notification: BidderBidRequestModel.BidResultNotificationModel
    ) -> BidderBidRequestModel.NotificationResponse:
        session = cls.get_request_session()
        resp = session.post(
            f'{rtb_bidder_api_url}/bid-requests/win-notified', json=jsonable_encoder(result_notification)
        )
        resp.raise_for_status()
        resp_model = BidderBidRequestModel.NotificationResponse(**(resp.json()))
        return resp_model
