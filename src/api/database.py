# Создаем таблицы при запуске приложения
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.config import settings

router = APIRouter(prefix="/db",tags=["База данных"])


# enpoint для проверки подключения
@router.get(
        "/"
        ,summary="Проверка подключения к базе данных")
async def root(db: AsyncSession = Depends(get_db)):
    return {
        "message": "Подключение к базе данных успешно!",
        "database": settings.DB_NAME,
        "host": settings.DB_HOST
    }