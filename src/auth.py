from authx import AuthX, AuthXConfig
from src.config import settings

# Настройка AuthX
auth_config = AuthXConfig(
    JWT_SECRET_KEY=settings.SECRET_KEY,
    JWT_ACCESS_COOKIE_NAME="my_access_token",
    JWT_TOKEN_LOCATION=["cookies"]
)

# Экземпляр AuthX, который будем использовать по всему проекту
auth = AuthX(config=auth_config)