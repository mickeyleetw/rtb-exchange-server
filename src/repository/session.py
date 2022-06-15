from collections import defaultdict

from adapters.bidder_server.adapter import BidderServiceAdapter
from adapters.bidder_server.model import BidderSessionResponseModel, EndBidderSessionModel, InitBidderSessionModel
from apps.session.model import InitSessionModel, SessionResponseModel
from core.enums import ResultEnum, SessionStatusEnum
from core.exception import InvalidStateTransitionException, ResourceNotFoundException
from schemas.session import BidderSchema, SessionSchema

session_map: dict[str, SessionSchema] = defaultdict()
bidder_map: dict[str, BidderSchema] = defaultdict()


class SessionRepo:

    @staticmethod
    async def init_bidder_session(
        bidder_endpoint: str, bidder_session: InitBidderSessionModel
    ) -> BidderSessionResponseModel:
        return await BidderServiceAdapter.init_bidder_session(
            rtb_bidder_api_url=bidder_endpoint, bidder_session=bidder_session
        )

    @staticmethod
    async def end_session(bidder_endpoint: str, bidder_session: EndBidderSessionModel) -> BidderSessionResponseModel:
        return await BidderServiceAdapter.end_bidder_session(
            rtb_bidder_api_url=bidder_endpoint, bidder_session=bidder_session
        )

    @staticmethod
    async def convert_bidder_session_response_to_bidder_schema_map(bidder_payload: dict, bidder_resp: dict):
        bidder = BidderSchema(
            name=bidder_payload.name,
            endpoint=bidder_payload.endpoint,
            session_id=bidder_resp['session_id'],
            session_status=bidder_resp['status']
        )
        bidder_map[bidder_payload.name] = bidder
        return bidder_map

    @staticmethod
    async def update_bidder_session_schema(bidder: BidderSchema, update_bidder_data: dict):
        bidder.session_id = update_bidder_data['session_id']
        bidder.session_status = update_bidder_data['status']
        return bidder

    @staticmethod
    def create_session(session_data: InitSessionModel, bidder_resp_map: dict) -> SessionSchema:
        data = SessionSchema(
            session_id=session_data.id,
            status=SessionStatusEnum.OPENED,
            estimated_traffic=session_data.estimated_traffic,
            bidders=[
                SessionRepo.convert_bidder_session_response_to_bidder_schema_map(
                    bidder_payload=bidder, bidder_resp=bidder_resp_map[bidder.name]
                ) for bidder in session_data.bidders
            ],
            budget=session_data.bidder_setting.budget,
            impression_goal=session_data.bidder_setting.impression_goal
        )
        session_map[session_data.id] = data
        return data

    @staticmethod
    def update_session(session: SessionSchema, bidder_resp_map: dict) -> SessionSchema:
        session['status'] = SessionStatusEnum.CLOSED
        for bidder in session['bidders']:
            for name, schema in bidder.items():
                bidder_name = list(name)[0]
                bidder_schema = list(schema)[0]
                bidder = SessionRepo.update_bidder_session_schema(
                    bidder=bidder_schema, update_bidder_data=bidder_resp_map[bidder_name]
                )
        return session

    @staticmethod
    async def convert_session_response_to_model(session: SessionSchema):
        return SessionResponseModel(
            session_id=session.session_id,
            status=session.status,
            estimated_traffic=session.estimated_traffic,
            bidders=session.bidders,
            result=ResultEnum.ALLOWED
        )

    @staticmethod
    def get_session(session_id: str) -> SessionSchema:
        session = session_map.get(session_id, None)
        if not session:
            raise ResourceNotFoundException('Session')
        return session

    @staticmethod
    def check_session_status_is_valid(session: SessionSchema):
        if session.status != SessionStatusEnum.OPENED:
            raise InvalidStateTransitionException()
