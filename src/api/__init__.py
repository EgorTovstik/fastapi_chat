from fastapi import APIRouter

from src.api.users import router as users_router
from src.api.chats import router as chats_router
from src.api.messages import router as msg_router
from src.api.database import router as db_router

mainRouter = APIRouter()

mainRouter.include_router(users_router)
mainRouter.include_router(chats_router)
mainRouter.include_router(msg_router)
mainRouter.include_router(db_router)