from uuid import UUID

from fastapi import APIRouter, Depends, Response

from core.response import default_responses
from repository.session import cookie

from .model import InitSessionModel, SessionResponseModel

router = APIRouter(prefix='/sessions', tags=['Session'], responses=default_responses)


@router.post('/init', response_model=SessionResponseModel)
async def init_session(data: InitSessionModel, response: Response) -> SessionResponseModel:
    # TODO: to be implemented
    pass
    # session_id=data.session_id
    # new_data=data.dict()
    # new_data.pop(session_id)
    # await backend.create(session_id, new_data)
    # cookie.attach_to_response(response, session_id)


@router.post('/end', response_model=SessionResponseModel)
async def end_session(response: Response, session_id: UUID = Depends(cookie)) -> SessionResponseModel:
    # TODO: to be implemented
    pass

    # await backend.delete(session_id)
    # cookie.delete_from_response(response)
