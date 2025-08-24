from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Импорты из проекта
from src.auth import auth
from src.database import get_db
from src.models.users import User as UserModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Получение текущего пользователя из БД
async def get_current_user(
    token_data: dict = Depends(auth.get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Получает текущего аутентифицированного пользователя из JWT (cookie)
    """
    try:
        # В payload токена обычно лежит "sub" = username или user_id
        username = token_data.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не удалось извлечь пользователя из токена"
            )

        query = select(UserModel).filter(UserModel.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        
        return user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ошибка аутентификации: {str(e)}"
        )
