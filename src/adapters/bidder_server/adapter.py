import functools
import os
from json import JSONDecodeError
from typing import Callable

import requests
from fastapi import status
from fastapi.encoders import jsonable_encoder
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from adapters.bidder_server.model import BidderSessionResponseModel, EndBidderSessionModel, InitBidderSessionModel
from core.enums import ErrorCode
from core.exception import BidderServiceException

MOUNT_PREFIX = os.getenv('MOUNT_PREFIX', 'http://')
RTB_BIDDER_API_URL = os.getenv('BIDDER_API_URL', 'http://localhost:3002/')
RTB_BIDDER_API_RETIRES = 1


def http_error_handler(func: Callable):

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise BidderServiceException(code=ErrorCode.BIDDER_API_3002_CONNECTION_ERROR, msg=str(e))
        except requests.exceptions.HTTPError as e:
            try:
                data = e.response.json(strict=False)
                msg = f"{data['code']}, {data['message']}"
            except (JSONDecodeError, KeyError):
                msg = e.response.text
            raise BidderServiceException(msg)

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

    @classmethod
    @http_error_handler
    async def init_bidder_session(
        cls, rtb_bidder_api_url: str, bidder_session: InitBidderSessionModel
    ) -> BidderSessionResponseModel:
        session = cls.get_request_session()
        resp = session.post(f'{rtb_bidder_api_url}/sessions/init', json=jsonable_encoder(bidder_session))
        resp.raise_for_status()
        bidder_session_response = BidderSessionResponseModel(**(resp.json()))
        return bidder_session_response

    @classmethod
    @http_error_handler
    async def end_bidder_session(
        cls, rtb_bidder_api_url: str, bidder_session: EndBidderSessionModel
    ) -> BidderSessionResponseModel:
        session = cls.get_request_session()
        resp = session.post(f'{rtb_bidder_api_url}/sessions/end', json=jsonable_encoder(bidder_session))
        resp.raise_for_status()
        bidder_session_response = BidderSessionResponseModel(**(resp.json()))
        return bidder_session_response
