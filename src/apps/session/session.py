from collections import defaultdict

from fastapi import APIRouter
from starlette import status

from adapters.bidder_server.model import BidderSessionModel
from apps.session.model import EndSessionModel, InitSessionModel, SessionResponseModel
from core.enums import ResultEnum, SessionStatusEnum
from core.exception import BidderServiceException, NoBidderResponseException
from core.response import default_responses, response_201, response_403, response_404, response_406, response_409
from repository.session import SessionRepo
from schemas.session import SessionSchema

router = APIRouter(prefix='/sessions', tags=['Session'], responses=default_responses)


@router.post(
    '/init',
    response_model=SessionResponseModel,
    responses={
        **response_201(SessionSchema, 'session'),
        **response_406(),
        **response_409(),
    }
)
async def init_session(data: InitSessionModel) -> SessionResponseModel:
    # NOTE: the checking may cause some problem if usr input same session_id when
    # previous session isn't complete (since this is async api)
    SessionRepo.check_session_is_existed(session_id=data.session_id)
    bidder_session = BidderSessionModel.InitSessionModel(
        session_id=data.session_id,
        estimated_traffic=data.estimated_traffic,
        budget=data.bidder_setting.budget,
        impression_goal=data.bidder_setting.impression_goal
    )

    bidder_resp_map: dict[str, BidderSessionModel.SessionResponseModel] = defaultdict()

    for bidder in data.bidders:
        bidder_session_resp = await SessionRepo.init_bidder_session(
            bidder_endpoint=bidder.endpoint, bidder_session=bidder_session
        )
        if type(bidder_session_resp) != BidderServiceException:
            if bidder_session_resp.result == ResultEnum.DENIED:
                continue
            elif bidder_session_resp.exchange_session_id != data.session_id:
                continue
            else:
                bidder_resp_map[bidder.name] = bidder_session_resp
    if len(bidder_resp_map) == 0:
        raise NoBidderResponseException()
    new_session = SessionRepo.create_session(session_data=data, bidder_resp_map=bidder_resp_map)
    return SessionRepo.convert_session_response_to_model(session=new_session)


@router.post(
    '/end',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=SessionResponseModel,
    responses={
        **response_404('session'),
        **response_403(),
    }
)
async def end_session(data: EndSessionModel) -> SessionResponseModel:
    session = SessionRepo.get_session(session_id=data.session_id)
    SessionRepo.check_session_status_is_valid(session=session)
    bidder_resp_map: dict[str, BidderSessionModel.SessionResponseModel] = defaultdict()
    for bidder in session.bidders:
        name = list(bidder.keys())[0]
        bidder = list(bidder.values())[0]
        bidder_session_resp = await SessionRepo.end_bidder_session(bidder_endpoint=bidder.endpoint, data=data)
        if type(bidder_session_resp) != BidderServiceException:
            bidder_resp_map[name] = bidder_session_resp
        else:
            bidder_resp_map[name] = BidderSessionModel.SessionResponseModel(
                exchange_session_id=data.session_id,
                status=SessionStatusEnum.UNKNOWN,
            )
    session = SessionRepo.update_session(session=session, bidder_resp_map=bidder_resp_map)
    return SessionRepo.convert_session_response_to_model(session=session)
