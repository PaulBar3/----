from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """Базовая схема товара."""
    name: str = Field(..., min_length=1, max_length=200, description="Название товара")
    description: str = Field(default="", max_length=2000, description="Описание товара")
    price: int = Field(..., gt=0, description="Цена в рублях")
    emoji: str = Field(default="🍗", max_length=10, description="Эмодзи товара")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Название не может быть пустым')
        return v.strip()
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Цена должна быть положительной')
        return v


class ProductCreate(ProductBase):
    """Схема для создания товара."""
    pass


class ProductUpdate(BaseModel):
    """Схема для обновления товара."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[int] = Field(None, gt=0)
    emoji: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Название не может быть пустым')
        return v.strip() if v else v


class ProductResponse(ProductBase):
    """Схема ответа с товаром."""
    id: int
    image: str = ""
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Схема списка товаров."""
    items: list[ProductResponse]
    total: int
