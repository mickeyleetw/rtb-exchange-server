from adapters.bidder_server.adapter import BidderServiceAdapter
from adapters.bidder_server.model import BidderSessionResponseModel, InitBidderSessionModel


class SessionRepo:

    @staticmethod
    async def init_bidder_session(
        bidder_endpoint: str, bidder_session: InitBidderSessionModel
    ) -> BidderSessionResponseModel:
        return await BidderServiceAdapter.init_bidder_session(
            rtb_bidder_api_url=bidder_endpoint, bidder_session=bidder_session
        )
