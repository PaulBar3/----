from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import declarative_base
from app.core.config import get_settings

settings = get_settings()

# Асинхронный движок для SQLite
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    """Зависимость для получения асинхронной сессии БД."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Инициализация базы данных (создание таблиц)."""
    async with engine.begin() as conn:
        # Импортируем модели для регистрации в Base.metadata
        from app.models.product import ProductModel  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
