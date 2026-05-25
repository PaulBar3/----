import os
from typing import Annotated, Optional
from fastapi import APIRouter, Request, Form, File, UploadFile, Depends, HTTPException, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.auth import check_admin_basic, get_settings
from app.models.product import ProductModel
from app.utils.image_handler import save_product_image, delete_product_image

router = APIRouter()
templates = Jinja2Templates(directory="templates")
settings = get_settings()


@router.get("/admin")
async def admin_panel(
    request: Request,
    credentials: Annotated[str, Depends(check_admin_basic)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Панель администратора."""
    result = await db.execute(select(ProductModel))
    products = result.scalars().all()
    
    return templates.TemplateResponse(request, "admin.html", {
        "products": products,
        "username": credentials
    })


@router.post("/admin/add")
async def admin_add_product(
    request: Request,
    name: Annotated[str, Form()],
    price: Annotated[int, Form()],
    description: Annotated[str, Form()] = "",
    emoji: Annotated[str, Form()] = "🍗",
    image: Annotated[Optional[UploadFile], File()] = None,
    credentials: Annotated[Optional[str], Depends(check_admin_basic)] = None,
    db: Annotated[Optional[AsyncSession], Depends(get_db)] = None,
):
    """Добавление нового товара (Post/Redirect/Get)."""
    try:
        # Валидация данных
        if not name or not name.strip():
            raise HTTPException(status_code=400, detail="Название товара обязательно")
        
        if price <= 0:
            raise HTTPException(status_code=400, detail="Цена должна быть положительной")
        
        # Сохраняем фото
        image_filename = ""
        if image and image.filename and image.filename.strip():
            image_filename = save_product_image(image)
        
        # Создаём товар
        product = ProductModel(
            name=name.strip(),
            description=description.strip() if description else "",
            price=price,
            emoji=emoji,
            image=image_filename
        )
        db.add(product)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    return RedirectResponse(url="/admin?message=Товар добавлен! ✅", status_code=303)


@router.post("/admin/delete/{product_id}")
async def admin_delete_product(
    product_id: int,
    request: Request,
    credentials: Annotated[Optional[str], Depends(check_admin_basic)] = None,
    db: Annotated[Optional[AsyncSession], Depends(get_db)] = None,
):
    """Удаление товара (Post/Redirect/Get)."""
    result = await db.execute(select(ProductModel).where(ProductModel.id == product_id))
    product = result.scalar_one_or_none()
    
    if product:
        delete_product_image(product.image)
        await db.delete(product)
        await db.commit()
    
    return RedirectResponse(url="/admin?message=Товар удалён 🗑️", status_code=303)


@router.post("/admin/toggle/{product_id}")
async def admin_toggle_product(
    product_id: int,
    request: Request,
    credentials: Annotated[Optional[str], Depends(check_admin_basic)] = None,
    db: Annotated[Optional[AsyncSession], Depends(get_db)] = None,
):
    """Переключение статуса товара (Post/Redirect/Get)."""
    result = await db.execute(select(ProductModel).where(ProductModel.id == product_id))
    product = result.scalar_one_or_none()
    
    if product:
        product.is_active = not product.is_active
        await db.commit()
    
    status_text = "активен" if product.is_active else "скрыт"
    return RedirectResponse(url=f"/admin?message=Товар {status_text} ✓", status_code=303)


@router.post("/admin/edit/{product_id}")
async def admin_edit_product(
    product_id: int,
    request: Request,
    name: Annotated[str, Form()],
    price: Annotated[int, Form()],
    description: Annotated[str, Form()] = "",
    emoji: Annotated[str, Form()] = "🍗",
    image: Annotated[Optional[UploadFile], File()] = None,
    credentials: Annotated[Optional[str], Depends(check_admin_basic)] = None,
    db: Annotated[Optional[AsyncSession], Depends(get_db)] = None,
):
    """Редактирование товара (Post/Redirect/Get)."""
    result = await db.execute(select(ProductModel).where(ProductModel.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    # Валидация
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Название товара обязательно")
    
    if price <= 0:
        raise HTTPException(status_code=400, detail="Цена должна быть положительной")
    
    product.name = name.strip()
    product.description = description.strip() if description else ""
    product.price = price
    product.emoji = emoji
    
    # Если загрузили новое фото
    if image and image.filename and image.filename.strip():
        delete_product_image(product.image)
        image_filename = save_product_image(image)
        product.image = image_filename
    
    await db.commit()
    
    return RedirectResponse(url=f"/admin?message=Товар обновлён! ✅", status_code=303)
