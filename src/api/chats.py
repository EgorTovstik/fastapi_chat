from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from authx import TokenPayload

# Импорты из проекта
from src.auth import auth
from src.database import get_db
from src.models.chats import Chat
from src.schemas.chats import *
from src.models.users import User as userModel


router = APIRouter(prefix="/chats", tags=["Чаты"])

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    payload: TokenPayload = Depends(auth.access_token_required),
):
    query = select(userModel).filter(userModel.username == payload.sub)
    result = await db.execute(query)
    current_user = result.scalar_one_or_none()
    return current_user

# Создание чата
@router.post("/create-chat", response_model=ChatBase, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat: ChatCreate,
    chat_members: List[ChatMemberCreate],
    db: AsyncSession = Depends(get_db),
):
    current_user = get_current_user()
    # Проверка типа чата
    if chat.type not in ['private', 'group', 'channel']:
        raise HTTPException(status_code=400, detail="Invalid chat type")

    # Для private чата проверяем участников
    if chat.type == 'private':
        if len(chat_members) != 1:
            raise HTTPException(status_code=400, detail="Private chat должен содержать ровно одного другого пользователя")
        participant_id = chat_members[0].user_id

        if participant_id == current_user.id:
            raise HTTPException(status_code=400, detail="Нельзя создать чат с самим собой")

        # Проверяем, существует ли пользователь
        result = await db.execute(select(User).filter(User.id == participant_id))
        participant = result.scalar_one_or_none()
        if not participant:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Проверяем, есть ли уже private чат между этими пользователями
        result = await db.execute(
            select(Chat)
            .join(ChatMember)
            .filter(Chat.type == 'private')
            .filter(ChatMember.user_id.in_([current_user.id, participant_id]))
        )
        existing_chat = result.scalar_one_or_none()
        if existing_chat:
            return existing_chat

        # Создаём чат
        chat_name = f"{current_user.username} + {participant.username}"
        new_chat = Chat(type='private', name=chat_name, created_by=current_user.id)
        db.add(new_chat)
        await db.commit()
        await db.refresh(new_chat)

        # Добавляем участников
        members = [
            ChatMember(chat_id=new_chat.id, user_id=current_user.id, role="owner"),
            ChatMember(chat_id=new_chat.id, user_id=participant_id, role=chat_members[0].role)
        ]
        db.add_all(members)
        await db.commit()
        return new_chat

    # Для группового или канального чата
    new_chat = Chat(type=chat.type, name=chat.name, created_by=current_user.id)
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)

    # Добавляем участников, включая создателя
    members = [ChatMember(chat_id=new_chat.id, user_id=current_user.id, role="owner")]
    for member in chat_members:
        if member.user_id == current_user.id:
            continue  # создатель уже добавлен
        # Проверяем, существует ли пользователь
        result = await db.execute(select(User).filter(User.id == member.user_id))
        user = result.scalar_one_or_none()
        if not user:
            continue  # пропускаем несуществующих пользователей
        members.append(ChatMember(chat_id=new_chat.id, user_id=member.user_id, role=member.role))

    db.add_all(members)
    await db.commit()

    return new_chat