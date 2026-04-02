from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.product import ProductModel

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_products(db: Session):
    return db.query(ProductModel).filter(ProductModel.is_active == True).all()


@router.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    products = get_products(db)
    return templates.TemplateResponse(request, "index.html", {"products": products[:3]})


@router.get("/menu")
async def menu(request: Request, db: Session = Depends(get_db), message: str | None = None):
    products = get_products(db)
    return templates.TemplateResponse(request, "menu.html", {
        "products": products,
        "message": message
    })
