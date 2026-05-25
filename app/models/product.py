from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()


class ProductModel(Base):
    """Модель товара."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, default="")
    price = Column(Integer, nullable=False)
    image = Column(String(500), default="")
    emoji = Column(String(10), default="🍗")
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Преобразование модели в словарь."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image": self.image,
            "emoji": self.emoji,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
