from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Импорты из проекта
from src.database import get_db
from src.models.users import User as UserModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функция хэширования пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Функця проверки пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Получение текущего пользователя
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

async def get_current_user(
        token: str = Depends(oauth2_scheme), 
        db: AsyncSession = Depends(get_db)
):
    from src.main import auth # Перенести в get_current_user если ошибка будет
    try:
        payload = auth.decode_access_token(token)
        username = payload.get("uid")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен")
        
        query = select(UserModel).filter(UserModel.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
        return user
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен")