from authx import AuthX, AuthXConfig
from src.config import settings

# Настройка конфигурации AuthX
auth_config = AuthXConfig(
    JWT_SECRET_KEY=settings.SECRET_KEY,
    JWT_ACCESS_COOKIE_NAME="my_access_token",  # Имя куки
    JWT_TOKEN_LOCATION=["cookies"],            # ✅ токен берём из cookies
    JWT_COOKIE_CSRF_PROTECT=False,             # Отключаем CSRF для простоты
    JWT_ACCESS_COOKIE_PATH="/",                # Путь для куки
    JWT_COOKIE_DOMAIN=None,                    # Домен куки (можно задать)
    JWT_COOKIE_SECURE=False,                   # False для HTTP, True для HTTPS
    JWT_COOKIE_SAMESITE="lax",                 # Политика SameSite
)

# Экземпляр AuthX, который будем использовать по всему проекту
auth = AuthX(config=auth_config)