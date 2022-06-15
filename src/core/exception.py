from fastapi import status

from core.enums import ErrorCode


class BaseException_(Exception):
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = ErrorCode.GENERAL_1001_UNEXPECTED_ERROR
    message = 'Unexpected'

    def __init__(self, msg=None, **kwargs):
        if not msg:
            msg = self.message
        for k, v in kwargs.items():
            setattr(self, k, v)

        super().__init__(msg)


class BidderServiceException(BaseException_):
    http_status = status.HTTP_400_BAD_REQUEST
    code = ErrorCode.BIDDER_API_3001_UNKNOWN_ERROR
    message = 'Bidder API service error'

    def __init__(self, msg=None, **kwargs):
        msg = f'{self.message} ({msg})'
        super().__init__(msg, **kwargs)
        self.message = msg


class ResourceNotFoundException(BaseException_):

    def __init__(self, subject: str):
        super().__init__(
            code=ErrorCode.RESOURCE_2001_NOT_FOUND,
            http_status=status.HTTP_404_NOT_FOUND,
            message=f'{subject} not found'
        )


class EmptyQueryParamsException(BaseException_):

    def __init__(self, msg: str):
        super().__init__(
            code=ErrorCode.GENERAL_1003_REQUEST_VALIDATION_FAILED,
            http_status=status.HTTP_428_PRECONDITION_REQUIRED,
            message=msg
        )


class InvalidStateTransitionException(BaseException_):

    def __init__(self):
        super().__init__(
            code=ErrorCode.GENERAL_1004_INVALID_STATE_TRANSITION,
            http_status=status.HTTP_403_FORBIDDEN,
            message='state error'
        )
