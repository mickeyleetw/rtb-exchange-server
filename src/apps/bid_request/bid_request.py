from fastapi import APIRouter
from starlette import status

from core.response import default_responses, response_201, response_404

from .model import CreateBidRequestModel, RetrieveBidResultModel

router = APIRouter(prefix="", tags=['Bid Request'], responses=default_responses)


@router.post(
    '/bid_requests',
    status_code=status.HTTP_201_CREATED,
    response_model=RetrieveBidResultModel,
    responses={
        **response_404('Bid Request'),
        **response_201(RetrieveBidResultModel, 'Bid Request')
    }
)
async def fire_bid_request(data: CreateBidRequestModel) -> RetrieveBidResultModel:
    # TODO: to be implemented
    # 1. check session_response is allowed or not
    # 2. fire-bid request and exchange should follow the response by bid-request to call bider-server POST bid request
    # 3. collect the bidder-response and determine who won the bid and return to response to client

    pass
