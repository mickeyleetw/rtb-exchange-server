import enum


@enum.unique
class ErrorCode(enum.IntEnum):
    GENERAL_1001_UNEXPECTED_ERROR = 1001
    GENERAL_1002_REQUEST_VALIDATION_FAILED = 1002
    GENERAL_1003_INVALID_STATE_TRANSITION = 1003
    GENERAL_1004_UNAUTHORIZED_BEHAVIOR = 1004

    RESOURCE_2001_NOT_FOUND = 2001

    BIDDER_API_3001_UNKNOWN_ERROR = 3001
    BIDDER_API_3002_CONNECTION_ERROR = 3002


class StrEnum(str, enum.Enum):
    pass


class ResultEnum(StrEnum):
    ALLOWED = 'ok'


class SessionStatusEnum(StrEnum):
    OPENED = 'opened'
    UNKNOWN = 'unknown'
    CLOSED = 'closed'
