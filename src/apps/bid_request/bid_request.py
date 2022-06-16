from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter
from starlette import status

from adapters.bidder_server.model import BidderBidRequestModel
from apps.bid_request.model import CreateBidRequestModel, RetrieveBidResultModel
from core.exception import BidderServiceException, NoBidderResponseException
from core.response import default_responses, response_201, response_403, response_404, response_406, response_409
from repository.bid_request import BidRequestRepo
from repository.session import SessionRepo
from schemas.bid_request import BidRequestSchema

router = APIRouter(prefix="", tags=['Bid Request'], responses=default_responses)


@router.post(
    '/bid_requests',
    status_code=status.HTTP_201_CREATED,
    response_model=RetrieveBidResultModel,
    responses={
        **response_404('session'),
        **response_409(),
        **response_406(),
        **response_403(),
        **response_201(BidRequestSchema, 'bid Request')
    }
)
async def fire_bid_request(data: CreateBidRequestModel) -> RetrieveBidResultModel:
    session = SessionRepo.get_session(session_id=data.session_id)
    SessionRepo.check_session_status_is_valid(session=session)

    # NOTE: the checking may cause some problem if usr input same request_id when
    # previous request isn't complete (since this is async api)
    BidRequestRepo.check_bid_request_is_existed(bid_request_id=data.request_id)

    bidder_bid_request = BidderBidRequestModel.CreateBidRequestModel(**data.dict())

    bidder_resp_map: dict[str, dict] = defaultdict()
    bidder_resp_queue = []
    time_out = (data.timeout_ms) / 10000

    for bidder in session.bidders:
        bidder_schema = list(bidder.values())[0]
        bidder_bid_resp = await BidRequestRepo.create_bidder_bid_request(
            bidder_endpoint=bidder_schema.endpoint, bidder_bid_request=bidder_bid_request, time_out=time_out
        )
        if type(bidder_bid_resp) != BidderServiceException:
            if bidder_bid_resp.session_id != data.session_id:
                continue
            elif bidder_bid_resp.request_id != data.request_id:
                continue
            elif bidder_bid_resp.price < data.floor_price:
                continue
            else:
                resp = bidder_bid_resp.dict()
                resp['url'] = bidder_schema.endpoint
                bidder_resp_map[bidder_schema.name] = resp
                bidder_resp_queue.append(bidder_resp_map)

    with ThreadPoolExecutor() as executor:
        feature = executor.submit(BidRequestRepo.auction_function, bidder_resp_queue)
        bid_winner = feature.result()

    if len(bidder_resp_map) == 0:
        raise NoBidderResponseException()

    win_price = BidRequestRepo.get_second_hight_price(bidder_resp_map=bidder_resp_map)
    result_notification = BidderBidRequestModel.BidResultNotificationModel(
        session_id=data.session_id, request_id=data.request_id, clear_price=win_price
    )
    winner_resp = list(bid_winner.values())[0]
    win_bid_resp = await BidRequestRepo.bid_result_notified(
        bidder_endpoint=winner_resp['url'], result_notification=result_notification
    )

    if type(win_bid_resp) == BidderServiceException:
        bid_winner = None
    new_request = BidRequestRepo.create_bid_request(
        bid_request_data=data, bidder_resp_map=bidder_resp_map, winner=bid_winner
    )
    return BidRequestRepo.convert_bid_request_response_to_model(bid_request=new_request)
