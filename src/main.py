import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

# Импорты из проекта
from src.database import engine, Base
from src.api import mainRouter
from src.config import settings

# AuthX
from authx import AuthX, AuthXConfig

app = FastAPI(title='BL-chat')

# Путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent        # src/
PROJECT_DIR = BASE_DIR.parent                     # корень проекта

# Подключаем статические файлы (CSS, JS, images)
static_path = PROJECT_DIR / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Настраиваем шаблонизатор
templates_path = PROJECT_DIR / "templates"
templates = Jinja2Templates(directory=templates_path)

# Подключаем API роутеры
app.include_router(mainRouter)

# Настройка AuthX
auth_config = AuthXConfig(
    JWT_SECRET_KEY=settings.SECRET_KEY,
    JWT_ACCESS_COOKIE_NAME="my_access_token",
    JWT_TOKEN_LOCATION=["cookies"]
)
auth = AuthX(config=auth_config)

# Создаем таблицы при запуске приложения
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Главная страница - отдает index.html
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", 
        reload=True, 
        host=settings.APP_HOST, 
        port=settings.APP_PORT
    )
