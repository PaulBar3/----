import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from app.core.database import init_db
from app.routes.main import router as main_router
from app.routes.cart import router as cart_router
from app.routes.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # При запуске
    os.makedirs("static/uploads/products", exist_ok=True)
    await init_db()
    yield
    # При остановке (очистка ресурсов если нужно)


# Настройки
app = FastAPI(
    title="Курица-Гриль",
    description="Интернет-магазин куриц-гриль",
    version="1.0.0",
    lifespan=lifespan
)

templates = Jinja2Templates(directory="templates")

# Монтируем статику
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем роуты
app.include_router(main_router)
app.include_router(cart_router)
app.include_router(admin_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
