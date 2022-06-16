from collections import defaultdict

from adapters.bidder_server.adapter import BidderBidRequestAdapter
from adapters.bidder_server.model import BidderBidRequestModel
from apps.bid_request.model import CreateBidRequestModel, RetrieveBidResultModel
from core.exception import DuplicateRecordException
from schemas.bid_request import BidderSchema, BidRequestSchema

bid_request_map: dict[str, BidRequestSchema] = defaultdict()


class BidRequestRepo:

    @staticmethod
    def check_bid_request_is_existed(bid_request_id: str) -> bool:
        bid_request = bid_request_map.get(bid_request_id, None)
        if bid_request:
            raise DuplicateRecordException('bid request')

    @staticmethod
    async def create_bidder_bid_request(
        bidder_endpoint: str, bidder_bid_request: BidderBidRequestModel.CreateBidRequestModel, time_out: int
    ) -> BidderBidRequestModel.RetrieveBidResultModel:
        return await BidderBidRequestAdapter.bidder_create_bid_request(
            rtb_bidder_api_url=bidder_endpoint, bidder_bid_request=bidder_bid_request, time_out=time_out
        )

    @staticmethod
    async def bid_result_notified(
        bidder_endpoint: str, result_notification: BidderBidRequestModel.BidResultNotificationModel
    ) -> BidderBidRequestModel.NotificationResponse:
        return await BidderBidRequestAdapter.result_notified(
            rtb_bidder_api_url=bidder_endpoint, result_notification=result_notification
        )

    @staticmethod
    def convert_bidder_bid_request_resp_to_schema(name: str, bidder_map: dict):
        bidder_schema = BidderSchema(name=name, url=bidder_map['url'], price=bidder_map['price'])
        return bidder_schema

    @staticmethod
    def convert_winner_resp_to_schema(name: str, bidder_map: dict):
        bidder_schema = BidderSchema(
            name=list(name)[0], url=list(bidder_map)[0]['url'], price=list(bidder_map)[0]['price']
        )
        return bidder_schema

    @staticmethod
    def create_bid_request(
        bid_request_data: CreateBidRequestModel, bidder_resp_map: dict, winner: dict = None
    ) -> BidRequestSchema:
        bid_request_schema = BidRequestSchema(
            request_id=bid_request_data.request_id,
            session_id=bid_request_data.session_id,
            user_id=bid_request_data.user_id,
            floor_price=bid_request_data.floor_price,
            timeout=bid_request_data.timeout_ms,
            win_bid=BidRequestRepo.convert_winner_resp_to_schema(name=winner.keys(), bidder_map=winner.values())
            if winner else None,
            bid_responses=[
                BidRequestRepo.convert_bidder_bid_request_resp_to_schema(name=bidder_name, bidder_map=bidder_map)
                for bidder_name, bidder_map in bidder_resp_map.items()
            ]
        )
        bid_request_map[bid_request_data.request_id] = bid_request_schema
        return bid_request_schema

    @staticmethod
    def auction_function(bid_resp_queue: dict):
        bid_winner = None
        if len(bid_resp_queue) == 0:
            return bid_winner

        while len(bid_resp_queue) > 0:
            competitor = bid_resp_queue.pop(0)
            if not bid_winner:
                bid_winner = competitor
            else:
                competitor = bid_resp_queue.pop(0)
                if list(competitor.values())[0]['price'] > list(bid_winner.values())[0]['price']:
                    bid_winner = competitor
                else:
                    continue
        return bid_winner

    @staticmethod
    def get_second_hight_price(bidder_resp_map: dict):
        if len(bidder_resp_map) > 1:
            price_list = []
            for resp in list(bidder_resp_map.values()):
                price_list.append(a=resp['price'])
            price_list.sort()
            return price_list[-2]
        else:
            return list(bidder_resp_map.values())[0]['price']

    @staticmethod
    def convert_bid_request_response_to_model(bid_request: BidRequestSchema) -> RetrieveBidResultModel:
        return RetrieveBidResultModel(
            session_id=bid_request.session_id,
            request_id=bid_request.request_id,
            win_bid=bid_request.win_bid,
            bid_responses=bid_request.bid_responses
        )
