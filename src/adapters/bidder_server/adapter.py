import functools
import os
from json import JSONDecodeError
from typing import Callable

import requests
from fastapi import status
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.enums import ErrorCode
from core.exception import BidderServiceException

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
        session.mount(RTB_BIDDER_API_URL, HTTPAdapter(max_retries=retries))

        return session
