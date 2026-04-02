from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from app.core.database import engine, init_db
from app.routes.main import router as main_router
from app.routes.cart import router as cart_router
from app.routes.admin import router as admin_router

# Настройки
app = FastAPI(title="Курица-Гриль")
templates = Jinja2Templates(directory="templates")

# Создаём директории
os.makedirs("static/uploads/products", exist_ok=True)

# Монтируем статику
app.mount("/static", StaticFiles(directory="static"), name="static")

# Создание таблиц
init_db()

# Подключаем роуты
app.include_router(main_router)
app.include_router(cart_router)
app.include_router(admin_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
