from typing import Annotated
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.product import ProductModel

router = APIRouter()
templates = Jinja2Templates(directory="templates")


async def get_products(db: AsyncSession, limit: int | None = None):
    """Получение активных товаров."""
    query = select(ProductModel).where(ProductModel.is_active == True)
    
    if limit:
        query = query.limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/")
async def index(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    """Главная страница."""
    products = await get_products(db, limit=3)
    return templates.TemplateResponse(request, "index.html", {"products": products})


@router.get("/menu")
async def menu(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    message: str | None = None,
    error: str | None = None,
):
    """Страница меню."""
    products = await get_products(db)
    return templates.TemplateResponse(request, "menu.html", {
        "products": products,
        "message": message,
        "error": error
    })
