
from fastapi import APIRouter

from core.response import default_responses, response_404,response_201
from starlette import status

from .model import InitSessionModel,SessionResponseModel,EndSessionModel
router = APIRouter(prefix='/sessions', tags=['Session'], responses=default_responses)


@router.post(
    '/init',
    response_model=SessionResponseModel
)
async def init_session(data:InitSessionModel) -> SessionResponseModel:
    # TODO: to be implemented
    pass


@router.post(
    '/end',
    response_model=SessionResponseModel
)
async def end_session(data:EndSessionModel) -> SessionResponseModel:
    # TODO: to be implemented
    pass