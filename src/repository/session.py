from collections import defaultdict

from adapters.bidder_server.adapter import BidderSessionAdapter
from adapters.bidder_server.model import BidderSessionModel
from apps.session.model import BidderModel, InitSessionModel, SessionResponseModel
from core.enums import ResultEnum, SessionStatusEnum
from core.exception import DuplicateRecordException, InvalidStateTransitionException, ResourceNotFoundException
from schemas.session import BidderSchema, SessionSchema

session_map: dict[str, SessionSchema] = defaultdict()
bidder_map: dict[str, BidderSchema] = defaultdict()


class SessionRepo:

    @staticmethod
    async def init_bidder_session(
        bidder_endpoint: str, bidder_session: BidderSessionModel.InitSessionModel
    ) -> BidderSessionModel.SessionResponseModel:
        return await BidderSessionAdapter.init_bidder_session(
            rtb_bidder_api_url=bidder_endpoint, bidder_session=bidder_session
        )

    @staticmethod
    async def end_bidder_session(
        bidder_endpoint: str, data: BidderSessionModel.EndSessionModel
    ) -> BidderSessionModel.SessionResponseModel:
        return await BidderSessionAdapter.end_bidder_session(rtb_bidder_api_url=bidder_endpoint, data=data)

    @staticmethod
    def convert_bidder_session_response_to_bidder_schema_map(bidder_payload: dict, bidder_resp: dict):
        bidder = BidderSchema(
            name=bidder_payload.name,
            endpoint=bidder_payload.endpoint,
            session_id=bidder_resp.exchange_session_id,
            session_status=bidder_resp.status
        )
        bidder_map[bidder_payload.name] = bidder
        return bidder_map

    @staticmethod
    def update_bidder_schema(bidder: dict, update_bidder_data: SessionResponseModel):
        bidder['session_status'] = update_bidder_data.status
        return bidder

    @staticmethod
    def create_session(session_data: InitSessionModel, bidder_resp_map: dict) -> SessionSchema:
        data = SessionSchema(
            session_id=session_data.session_id,
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
        session_map[session_data.session_id] = data
        return data

    @staticmethod
    def update_session(session: SessionSchema, bidder_resp_map: dict) -> SessionSchema:
        session_dict = session.dict()
        session_dict['status'] = SessionStatusEnum.CLOSED
        for bidder in session_dict['bidders']:
            bidder_name = list(bidder.keys())[0]
            bidder_dict = list(bidder.values())[0]
            bidder = SessionRepo.update_bidder_schema(
                bidder=bidder_dict, update_bidder_data=bidder_resp_map[bidder_name]
            )
        return SessionSchema(**session_dict)

    @staticmethod
    def convert_bidder_response_to_model(bidder: BidderSchema):
        return BidderModel(name=bidder.name, endpoint=bidder.endpoint)

    @staticmethod
    def convert_session_response_to_model(session: SessionSchema):
        return SessionResponseModel(
            session_id=session.session_id,
            status=session.status,
            estimated_traffic=session.estimated_traffic,
            bidders=[
                SessionRepo.convert_bidder_response_to_model(bidder=list(bidder.values())[0])
                for bidder in session.bidders
            ],
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

    @staticmethod
    def check_session_is_existed(session_id: str) -> bool:
        session = session_map.get(session_id, None)
        if session and session.status == SessionStatusEnum.OPENED:
            raise DuplicateRecordException('session')
        # NOTE: not sure if session can be repeatably created with same session id
        elif session and session.status == SessionStatusEnum.CLOSED:
            raise DuplicateRecordException('session with same id')
