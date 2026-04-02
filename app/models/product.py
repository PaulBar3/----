from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    price = Column(Integer, nullable=False)
    image = Column(String(500), default="")
    emoji = Column(String(10), default="🍗")
    is_active = Column(Boolean, default=True)
    created_at = Column(String(50), default=lambda: datetime.now().isoformat())
