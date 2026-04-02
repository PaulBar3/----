from fastapi import APIRouter, Request, Form, File, UploadFile, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import check_admin
from app.models.product import ProductModel
from app.utils.image_handler import save_product_image, delete_product_image

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admin")
async def admin_panel(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(check_admin),
    db: Session = Depends(get_db)
):
    products = db.query(ProductModel).all()
    return templates.TemplateResponse(request, "admin.html", {
        "products": products,
        "username": credentials.username
    })


@router.post("/admin/add")
async def admin_add_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    price: int = Form(...),
    emoji: str = Form("🍗"),
    image: UploadFile = File(None),
    credentials: HTTPBasicCredentials = Depends(check_admin),
    db: Session = Depends(get_db)
):
    try:
        # Сохраняем фото
        image_filename = ""
        if image and image.filename and image.filename.strip():
            image_filename = save_product_image(image)

        # Создаём товар
        product = ProductModel(
            name=name,
            description=description,
            price=price,
            emoji=emoji,
            image=image_filename
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        products = db.query(ProductModel).all()
        return templates.TemplateResponse(request, "admin.html", {
            "request": request,
            "products": products,
            "username": credentials.username,
            "message": f"Товар '{name}' добавлен! ✅"
        })
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/delete/{product_id}")
async def admin_delete_product(
    product_id: int,
    request: Request,
    credentials: HTTPBasicCredentials = Depends(check_admin),
    db: Session = Depends(get_db)
):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if product:
        delete_product_image(product.image)
        db.delete(product)
        db.commit()

    products = db.query(ProductModel).all()
    return templates.TemplateResponse(request, "admin.html", {
        "request": request,
        "products": products,
        "username": credentials.username,
        "message": "Товар удалён 🗑️"
    })


@router.post("/admin/toggle/{product_id}")
async def admin_toggle_product(
    product_id: int,
    request: Request,
    credentials: HTTPBasicCredentials = Depends(check_admin),
    db: Session = Depends(get_db)
):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if product:
        product.is_active = not product.is_active
        db.commit()

    products = db.query(ProductModel).all()
    status_text = "активен" if product.is_active else "скрыт"
    return templates.TemplateResponse(request, "admin.html", {
        "request": request,
        "products": products,
        "username": credentials.username,
        "message": f"Товар {status_text} ✓"
    })


@router.post("/admin/edit/{product_id}")
async def admin_edit_product(
    product_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    price: int = Form(...),
    emoji: str = Form("🍗"),
    image: UploadFile = File(None),
    credentials: HTTPBasicCredentials = Depends(check_admin),
    db: Session = Depends(get_db)
):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    product.name = name
    product.description = description
    product.price = price
    product.emoji = emoji

    # Если загрузили новое фото
    if image and image.filename and image.filename.strip():
        delete_product_image(product.image)
        image_filename = save_product_image(image)
        product.image = image_filename

    db.commit()

    products = db.query(ProductModel).all()
    return templates.TemplateResponse(request, "admin.html", {
        "request": request,
        "products": products,
        "username": credentials.username,
        "message": f"Товар '{name}' обновлён! ✅"
    })
