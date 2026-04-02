from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.product import ProductModel

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Хранилище корзины (в памяти, для демо)
cart_storage: dict[str, list[dict]] = {}


@router.get("/cart")
async def cart(request: Request, session_id: str = "default", db: Session = Depends(get_db)):
    cart_items = cart_storage.get(session_id, [])
    total = 0
    items_with_details = []
    for item in cart_items:
        product = db.query(ProductModel).filter(ProductModel.id == item["product_id"]).first()
        if product:
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
    return templates.TemplateResponse(request, "cart.html", {
        "cart_items": items_with_details,
        "total": total
    })


@router.post("/cart/add")
async def add_to_cart(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(1),
    session_id: str = "default",
    db: Session = Depends(get_db)
):
    if session_id not in cart_storage:
        cart_storage[session_id] = []

    cart = cart_storage[session_id]
    existing = next((item for item in cart if item["product_id"] == product_id), None)

    if existing:
        existing["quantity"] += quantity
    else:
        cart.append({"product_id": product_id, "quantity": quantity})

    def get_products(db: Session):
        return db.query(ProductModel).filter(ProductModel.is_active == True).all()

    return templates.TemplateResponse(request, "menu.html", {
        "products": get_products(db),
        "message": "Товар добавлен в корзину! ✅"
    })


@router.post("/cart/clear")
async def clear_cart(request: Request, session_id: str = "default"):
    cart_storage[session_id] = []
    return RedirectResponse(url="/cart", status_code=303)
