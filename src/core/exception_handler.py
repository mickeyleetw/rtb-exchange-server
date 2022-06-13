from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.responses import JSONResponse

from core.exception import BaseException_
from core.response import ErrorCode


def add_exception_handlers(app: FastAPI):

    @app.exception_handler(Exception)
    async def exception_handler(_: Request, exception: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'message': 'internal error',
                'code': ErrorCode.GENERAL_1001_UNEXPECTED_ERROR
            }
        )

    @app.exception_handler(BaseException_)
    async def base_exception_handler(_: Request, exception: BaseException_):
        return JSONResponse(
            status_code=exception.http_status,
            content={
                'code': exception.code,
                'message': exception.message
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exception: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                'code': ErrorCode.GENERAL_1002_REQUEST_VALIDATION_FAILED,
                'message': str(exception),
            }
        )
