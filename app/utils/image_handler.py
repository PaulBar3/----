import uuid
import os
from PIL import Image
import io


def save_product_image(image_file) -> str:
    """Сохраняет изображение товара и возвращает имя файла."""
    # Создаём директорию если нет
    os.makedirs("static/uploads/products", exist_ok=True)
    
    image_filename = f"{uuid.uuid4().hex}_{image_file.filename}"
    image_path = f"static/uploads/products/{image_filename}"

    contents = image_file.read()
    img = Image.open(io.BytesIO(contents))

    # Конвертируем в JPEG если нужно
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    # Изменяем размер для оптимизации
    img.thumbnail((800, 800))
    img.save(image_path, "JPEG", quality=85)

    return image_filename


def delete_product_image(image_filename: str) -> None:
    """Удаляет изображение товара."""
    if image_filename:
        try:
            os.remove(f"static/uploads/products/{image_filename}")
        except OSError:
            pass
