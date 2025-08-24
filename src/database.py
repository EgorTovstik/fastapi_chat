from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings

#Создаем движок для подключения к БД
engine = create_async_engine(
    settings.DATABASE_URL,
    echo = False, # Показывает SQL запросы в консоли (отключить в production)
    future=True
)

# Создаем фабрику сессий для работы с БД
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии БД
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
