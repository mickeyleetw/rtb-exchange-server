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
    # should hit bidder-api to announce bid-request

    pass
