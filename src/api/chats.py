from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

# Импорты из проекта
from src.database import get_db
from src.models.chats import Chat, ChatMember
from src.models.users import User as UserModel
from src.schemas.chats import ChatCreate, ChatMemberCreate, ChatBase
from src.api.utils import get_current_user

router = APIRouter(prefix="/chats", tags=["Чаты"])

# Создание чата
@router.post("/create-chat", response_model=ChatBase, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat: ChatCreate,
    chat_members: List[ChatMemberCreate],
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)  # ← Текущий пользователь из зависимости
):
    """
    Создание нового чата
    
    Для private чата: автоматическое определение имени и проверка существующего чата
    Для group/channel: создание с указанным именем и участниками
    """
    # Проверка типа чата
    if chat.type not in ['private', 'group', 'channel']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Неверный тип чата. Допустимые значения: private, group, channel"
        )

    # Для private чата
    if chat.type == 'private':
        if len(chat_members) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Private chat должен содержать ровно одного другого пользователя"
            )
        
        participant_id = chat_members[0].user_id

        # Проверка: нельзя создать чат с самим собой
        if participant_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Нельзя создать чат с самим собой"
            )

        # Проверяем, существует ли пользователь-участник
        result = await db.execute(select(UserModel).filter(UserModel.id == participant_id))
        participant = result.scalar_one_or_none()
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Пользователь не найден"
            )

        # Проверяем, есть ли уже private чат между этими пользователями
        existing_chat_query = (
            select(Chat)
            .join(ChatMember, Chat.id == ChatMember.chat_id)
            .where(Chat.type == 'private')
            .where(ChatMember.user_id.in_([current_user.id, participant_id]))
            .group_by(Chat.id)
            .having(func.count(ChatMember.user_id) == 2)
        )
        
        result = await db.execute(existing_chat_query)
        existing_chat = result.scalar_one_or_none()
        
        if existing_chat:
            # Возвращаем существующий чат
            return existing_chat

        # Создаём новый private чат
        chat_name = f"{current_user.username} + {participant.username}"
        new_chat = Chat(
            type='private', 
            name=chat_name, 
            created_by=current_user.id
        )
        db.add(new_chat)
        await db.commit()
        await db.refresh(new_chat)

        # Добавляем участников (создателя и второго пользователя)
        members = [
            ChatMember(
                chat_id=new_chat.id, 
                user_id=current_user.id, 
                role="owner"
            ),
            ChatMember(
                chat_id=new_chat.id, 
                user_id=participant_id, 
                role=chat_members[0].role or "member"
            )
        ]
        db.add_all(members)
        await db.commit()
        
        return new_chat

    # Для группового или канального чата
    # Проверяем название для группового чата
    if chat.type == 'group' and not chat.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Групповой чат должен иметь название"
        )

    # Создаём групповой/канальный чат
    new_chat = Chat(
        type=chat.type, 
        name=chat.name, 
        created_by=current_user.id
    )
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)

    # Добавляем участников, включая создателя как владельца
    members = [ChatMember(
        chat_id=new_chat.id, 
        user_id=current_user.id, 
        role="owner"
    )]
    
    # Добавляем остальных участников
    for member in chat_members:
        if member.user_id == current_user.id:
            continue  # создатель уже добавлен
        
        # Проверяем, существует ли пользователь
        result = await db.execute(select(UserModel).filter(UserModel.id == member.user_id))
        user = result.scalar_one_or_none()
        if not user:
            continue  # пропускаем несуществующих пользователей
            
        members.append(ChatMember(
            chat_id=new_chat.id, 
            user_id=member.user_id, 
            role=member.role or "member"
        ))

    # Проверяем, что есть хотя бы создатель
    if len(members) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Чат должен содержать хотя бы одного участника"
        )

    db.add_all(members)
    await db.commit()
    await db.refresh(new_chat)

    return new_chat