from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import HTTPException, status, Depends
from app.core.config import ADMIN_USER, ADMIN_PASS

security = HTTPBasic()


def check_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USER or credentials.password != ADMIN_PASS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials
