from fastapi import APIRouter

from adapters.bidder_server.model import InitBidderSessionModel
from core.enums import ResultEnum
from core.response import default_responses, response_201, response_400
from repository.session import SessionRepo

from .model import EndSessionModel, InitSessionModel, SessionResponseModel

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
    for bidder in data.bidders:
        await SessionRepo.init_bidder_session(bidder_endpoint=bidder.endpoint, bidder_session=bidder_session)
    return SessionResponseModel(result=ResultEnum.ALLOWED)


@router.post('/end', response_model=SessionResponseModel)
async def end_session(data: EndSessionModel) -> SessionResponseModel:
    pass
