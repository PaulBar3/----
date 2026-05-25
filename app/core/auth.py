import hashlib
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import get_settings, Settings

settings = get_settings()

# Хэширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 схема для токенов
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

# HTTP Basic для простой аутентификации (legacy)
security_basic = HTTPBasic()


class TokenData(BaseModel):
    """Данные токена."""
    username: str | None = None
    exp: datetime | None = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хэширование пароля."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Создание JWT токена."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Получение текущего пользователя из токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Проверяем, что это администратор
    if username != settings.ADMIN_USERNAME:
        raise credentials_exception
    
    return username


async def check_admin_basic(
    credentials: HTTPBasicCredentials = Depends(security_basic)
) -> str:
    """Проверка администратора через HTTP Basic (для совместимости)."""
    correct_username = credentials.username == settings.ADMIN_USERNAME
    correct_password = verify_password(credentials.password, settings.ADMIN_PASSWORD_HASH)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
