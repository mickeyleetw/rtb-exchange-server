from collections import defaultdict

from fastapi import APIRouter
from starlette import status

from adapters.bidder_server.model import BidderSessionResponseModel, InitBidderSessionModel
from apps.session.model import EndSessionModel, InitSessionModel, SessionResponseModel
from core.enums import ErrorCode, SessionStatusEnum
from core.exception import BidderServiceException, UnauthorizedBehaviorException
from core.response import default_responses, response_201, response_400, response_403, response_404
from repository.session import SessionRepo

router = APIRouter(prefix='/sessions', tags=['Session'], responses=default_responses)


@router.post(
    '/init',
    response_model=SessionResponseModel,
    responses={
        **response_201(InitSessionModel, 'Session'),
        **response_400()
    }
)
async def init_session(data: InitSessionModel) -> SessionResponseModel:

    bidder_session = InitBidderSessionModel(
        session_id=data.session_id,
        estimated_traffic=data.estimated_traffic,
        budget=data.bidder_setting.budget,
        impression_goal=data.bidder_setting.impression_goal
    )

    bidder_resp_map: dict[str, BidderSessionResponseModel] = defaultdict()

    for bidder in data.bidders:
        bidder_session_resp = await SessionRepo.init_bidder_session(
            bidder_endpoint=bidder.endpoint, bidder_session=bidder_session
        )
        if type(bidder_session_resp) != type(BidderServiceException):
            if bidder_session_resp['exchange_session_id'] != data.session_id:
                raise UnauthorizedBehaviorException('invalid session id')
            else:
                bidder_resp_map[bidder.name] = bidder_session_resp
    new_session = SessionRepo.create_session(session_data=data, bidder_resp_map=bidder_resp_map)
    return SessionRepo.convert_session_response_to_model(session=new_session)


@router.post(
    '/end',
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=SessionResponseModel,
    responses={
        **response_404('Session'),
        **response_400(),
        **response_403(ErrorCode.GENERAL_1003_INVALID_STATE_TRANSITION, 'state error'),
    }
)
async def end_session(data: EndSessionModel) -> SessionResponseModel:
    session = SessionRepo.get_session(session_id=data.session_id)
    SessionRepo.check_session_status_is_valid(session=session)
    bidder_resp_map: dict[str, BidderSessionResponseModel] = defaultdict()
    for bidder in session.bidders:
        name = list(bidder.keys())[0]
        bidder = list(bidder.values())[0]
        bidder_session_resp = await SessionRepo.end_bidder_session(
            bidder_endpoint=bidder.endpoint, bidder_session=bidder.session_id
        )
        if type(bidder_session_resp) != type(BidderServiceException):
            bidder_resp_map[name] = bidder_session_resp
        else:
            bidder_resp_map[name] = {'session_id': bidder.session_id, 'session_status': SessionStatusEnum.UNKNOWN}
    session = SessionRepo.update_session(session=session, bidder_resp_map=bidder_resp_map)
    return SessionRepo.convert_session_response_to_model(session=session)
