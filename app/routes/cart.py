import uuid
from typing import Annotated
from fastapi import APIRouter, Request, Form, Depends, Cookie, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.product import ProductModel

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Временное хранилище корзины (в production использовать Redis)
cart_storage: dict[str, list[dict]] = {}


def generate_session_id() -> str:
    """Генерация уникального ID сессии."""
    return str(uuid.uuid4())


@router.get("/cart")
async def cart(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    session_id: Annotated[str | None, Cookie()] = None,
):
    """Просмотр корзины."""
    if not session_id:
        session_id = generate_session_id()
    
    cart_items = cart_storage.get(session_id, [])
    total = 0
    items_with_details = []
    
    for item in cart_items:
        result = await db.execute(select(ProductModel).where(ProductModel.id == item["product_id"]))
        product = result.scalar_one_or_none()
        
        if product and product.is_active:
            item_total = product.price * item["quantity"]
            total += item_total
            items_with_details.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "image": product.image,
                "emoji": product.emoji,
                "quantity": item["quantity"],
                "item_total": item_total
            })
    
    response = templates.TemplateResponse(request, "cart.html", {
        "cart_items": items_with_details,
        "total": total
    })
    
    if not request.cookies.get("session_id"):
        response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=86400 * 7)
    
    return response


@router.post("/cart/add")
async def add_to_cart(
    request: Request,
    product_id: Annotated[int, Form()],
    quantity: Annotated[int, Form()] = 1,
    session_id: Annotated[str | None, Cookie()] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Добавление товара в корзину (Post/Redirect/Get паттерн)."""
    if quantity < 1:
        quantity = 1
    
    # Проверяем существование товара
    result = await db.execute(select(ProductModel).where(ProductModel.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product or not product.is_active:
        return RedirectResponse(url="/menu?error=Товар не найден", status_code=303)
    
    if not session_id:
        session_id = generate_session_id()
    
    if session_id not in cart_storage:
        cart_storage[session_id] = []
    
    cart = cart_storage[session_id]
    existing = next((item for item in cart if item["product_id"] == product_id), None)
    
    if existing:
        existing["quantity"] += quantity
    else:
        cart.append({"product_id": product_id, "quantity": quantity})
    
    # Post/Redirect/Get - перенаправляем вместо возврата HTML
    response = RedirectResponse(url="/menu?message=Товар добавлен в корзину! ✅", status_code=303)
    if not request.cookies.get("session_id"):
        response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=86400 * 7)
    
    return response


@router.post("/cart/remove/{product_id}")
async def remove_from_cart(
    product_id: int,
    request: Request,
    session_id: Annotated[str | None, Cookie()] = None,
):
    """Удаление товара из корзины."""
    if session_id and session_id in cart_storage:
        cart = cart_storage[session_id]
        cart_storage[session_id] = [item for item in cart if item["product_id"] != product_id]
    
    return RedirectResponse(url="/cart", status_code=303)


@router.post("/cart/clear")
async def clear_cart(
    request: Request,
    session_id: Annotated[str | None, Cookie()] = None,
):
    """Очистка корзины."""
    if session_id and session_id in cart_storage:
        cart_storage[session_id] = []
    
    return RedirectResponse(url="/cart", status_code=303)


@router.post("/cart/update")
async def update_cart(
    request: Request,
    product_id: Annotated[int, Form()],
    quantity: Annotated[int, Form()],
    session_id: Annotated[str | None, Cookie()] = None,
):
    """Обновление количества товара в корзине."""
    if session_id and session_id in cart_storage:
        cart = cart_storage[session_id]
        existing = next((item for item in cart if item["product_id"] == product_id), None)
        
        if existing:
            if quantity <= 0:
                cart.remove(existing)
            else:
                existing["quantity"] = quantity
    
    return RedirectResponse(url="/cart", status_code=303)
