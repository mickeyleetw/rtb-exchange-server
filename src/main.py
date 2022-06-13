from fastapi import FastAPI

from apps.bid_request.bid_request import router as bid_router
from apps.session.session import router as session_router
from core.exception_handler import add_exception_handlers
from core.response import default_responses

app = FastAPI(title='SimpleRTB Exchange Server')
app.include_router(bid_router)
app.include_router(session_router)


@app.get("/root", tags=["Root"], responses=default_responses,include_in_schema=False)
async def root():
    return {'status': 0}


add_exception_handlers(app=app)
