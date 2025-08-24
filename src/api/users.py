from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

# Импорты из проекта
from src.database import get_db
from src.models.users import User as userModel
from src.schemas.users import *
from src.api.utils import *

router = APIRouter(prefix="/user", tags=["Пользователи"])

# Получение всех пользователей
@router.get(
    "/get-users",
    summary="Получение всех пользователей",
    responses={
        200: {"description": "Успешный возврат списка пользователей"},
        500: {"description": "Ошибка сервера при получении данных"}
    }
)
async def get_all_users(
    skip: Optional[int] = 0,
    limit: Optional[int] = 100,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Ограничиваем максимальный лимит для защиты от перегрузки
        if limit > 1000:
            limit = 1000
        
        query = select(userModel).offset(skip).limit(limit)
        
        result = await db.execute(query)
        
        users = result.scalars().all()

        return users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении пользователей: {str(e)}"
        )
    
# Авторизаия пользователя
@router.post(
        "/login",
        summary="Авторизация пользователя",
        responses={
            201: {"description": "Пользователь успешно авторизован"},
            401: {"description": "Пользователь не найден"},
            500: {"description": "Ошибка входа"}
        }
)
async def login(
    creds: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    from src.main import auth
    if len(creds.username) == 0 or len(creds.password) == 0:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Введите логин или пароль"
            )
    try:
        query = select(userModel).filter(userModel.username == creds.username)
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь с таким логином не найден"
            )

        if not verify_password(creds.password, existing_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный пароль"
            )
        
        token = auth.create_access_token(uid=existing_user.username)
        
        return {"access_token": token}


    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка входа: {str(e)}"
        )

# Регистрация пользователя
@router.post(
    "/register",
    summary="Добавить пользователя",
    responses={
        201: {"description": "Пользователь успешно создан"},
        400: {"description": "Пользователь с таким логином уже существует"},
        500: {"description": "Ошибка сервера при добавлении пользователя"}
    }
)
async def create_user(
    new_user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Проверим есть ли пользователь в системе
        query = select(userModel).filter(userModel.username == new_user.username)
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user: 
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким логином уже существует"
                )
        
        # Хэшируем пароль
        hashed_pw = hash_password(new_user.password)

        # Создадим пользователя
        user = userModel(
            username = new_user.username,
            name = new_user.name,
            password = hashed_pw
        )

        db.add(user)

        await db.commit()
        await db.refresh(user)

        return user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при добавлении пользователя: {str(e)}"
        )
    

