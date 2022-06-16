import enum


@enum.unique
class ErrorCode(enum.IntEnum):
    GENERAL_1001_UNEXPECTED_ERROR = 1001
    GENERAL_1002_REQUEST_VALIDATION_FAILED = 1002
    GENERAL_1003_INVALID_STATE_TRANSITION = 1003
    GENERAL_1004_DUPLICATE_RECORD = 1004
    GENERAL_1005_RESOURCE_NOT_FOUND = 1005
    GENERAL_1006_NO_BIDDER_RESPONSE = 1006

    BIDDER_API_2001_UNKNOWN_ERROR = 2001
    BIDDER_API_2002_CONNECTION_ERROR = 2002
    BIDDER_API_2003_REQUEST_TIME_OUT = 2003


class StrEnum(str, enum.Enum):
    pass


class ResultEnum(StrEnum):
    ALLOWED = 'ok'
    DENIED = 'no'


class SessionStatusEnum(StrEnum):
    OPENED = 'opened'
    UNKNOWN = 'unknown'
    CLOSED = 'closed'
