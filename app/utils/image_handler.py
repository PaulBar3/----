import uuid
import os
from PIL import Image
import io
from fastapi import UploadFile, HTTPException

from app.core.config import get_settings

settings = get_settings()


def save_product_image(image_file: UploadFile) -> str:
    """Сохраняет изображение товара и возвращает имя файла."""
    # Создаём директорию если нет
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Проверка типа файла
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_ext = os.path.splitext(image_file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый формат файла. Разрешены: {', '.join(allowed_extensions)}"
        )
    
    # Генерируем уникальное имя файла
    image_filename = f"{uuid.uuid4().hex}{file_ext}"
    image_path = os.path.join(settings.UPLOAD_DIR, image_filename)
    
    contents = image_file.read()
    
    # Проверка размера файла
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой. Максимальный размер: {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB"
        )
    
    img = Image.open(io.BytesIO(contents))
    
    # Конвертируем в JPEG если нужно (для совместимости)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    
    # Изменяем размер для оптимизации
    img.thumbnail((800, 800))
    img.save(image_path, "JPEG", quality=85, optimize=True)
    
    return image_filename


def delete_product_image(image_filename: str) -> None:
    """Удаляет изображение товара."""
    if image_filename:
        try:
            image_path = os.path.join(settings.UPLOAD_DIR, image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        except OSError as e:
            # Логируем ошибку но не прерываем работу
            print(f"Ошибка при удалении изображения {image_filename}: {e}")
