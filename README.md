# 🍗 Курица-Гриль - Интернет-магазин

Современное веб-приложение для продажи куриц-гриль с админ-панелью.

## 🚀 Особенности

### Для клиентов:
- Просмотр каталога товаров
- Добавление товаров в корзину
- Индивидуальная корзина для каждого пользователя (cookie-based сессии)
- Управление корзиной (добавление, удаление, обновление количества)

### Для администратора:
- Управление товарами (CRUD операции)
- Загрузка и обработка изображений
- Включение/выключение отображения товаров
- Безопасная аутентификация с хэшированием паролей

## 🛠 Технологии

- **Backend**: FastAPI (асинхронный)
- **Database**: SQLite + SQLAlchemy (async)
- **Templates**: Jinja2
- **Images**: Pillow
- **Auth**: HTTP Basic + bcrypt хэширование
- **Validation**: Pydantic v2
- **Package Manager**: uv / pip

## 📁 Структура проекта

```
/workspace
├── main.py                 # Точка входа приложения
├── app/
│   ├── core/
│   │   ├── config.py       # Настройки (pydantic-settings)
│   │   ├── database.py     # Асинхронная БД конфигурация
│   │   └── auth.py         # Аутентификация и хэширование
│   ├── models/
│   │   └── product.py      # SQLAlchemy модели
│   ├── schemas/
│   │   └── product.py      # Pydantic схемы валидации
│   ├── routes/
│   │   ├── main.py         # Основные страницы
│   │   ├── cart.py         # Корзина (Post/Redirect/Get)
│   │   └── admin.py        # Админ-панель
│   └── utils/
│       └── image_handler.py # Обработка изображений
├── templates/              # Jinja2 шаблоны
├── static/                 # Статические файлы
└── .env.example           # Пример переменных окружения
```

## 🔧 Установка и запуск

### 1. Клонирование и установка зависимостей

```bash
# Через uv (рекомендуется)
uv sync

# Или через pip
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
cp .env.example .env
# Отредактируйте .env, особенно SECRET_KEY и ADMIN_PASSWORD_HASH
```

### 3. Запуск приложения

```bash
# Через start.sh
./start.sh

# Или напрямую
python main.py

# Или через uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔐 Безопасность

### Пароль администратора по умолчанию:
- **Логин**: `admin`
- **Пароль**: `admin123`

⚠️ **ВАЖНО**: В production обязательно измените пароль!

### Генерация хэша пароля:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])
hashed = pwd_context.hash("your_new_password")
# Добавьте hashed в ADMIN_PASSWORD_HASH в .env
```

## ✅ Улучшения в этой версии

### Исправленные ошибки:
1. **Общая корзина для всех** → Индивидуальные сессии через cookie
2. **Синхронная БД в async приложении** → Полностью асинхронный SQLAlchemy
3. **Hardcoded пароли** → Хэширование bcrypt + переменные окружения
4. **Возврат HTML после POST** → Post/Redirect/Get паттерн
5. **Отсутствие валидации** → Pydantic схемы с валидаторами
6. **Утечка памяти** → Правильное управление сессиями БД

### Лучшие практики FastAPI:
- ✅ Асинхронные handlers (`async def`)
- ✅ Type hints с `Annotated`
- ✅ Зависимости через `Depends()`
- ✅ Pydantic v2 схемы для валидации
- ✅ Settings management через pydantic-settings
- ✅ Lifespan events для инициализации
- ✅ Proper error handling с HTTPException
- ✅ RESTful редиректы после POST операций

## 📝 API Endpoints

### Публичные:
- `GET /` - Главная страница
- `GET /menu` - Каталог товаров
- `GET /cart` - Корзина
- `POST /cart/add` - Добавить в корзину
- `POST /cart/remove/{id}` - Удалить из корзины
- `POST /cart/update` - Обновить количество
- `POST /cart/clear` - Очистить корзину

### Админ-панель (требуется аутентификация):
- `GET /admin` - Панель управления
- `POST /admin/add` - Добавить товар
- `POST /admin/edit/{id}` - Редактировать товар
- `POST /admin/delete/{id}` - Удалить товар
- `POST /admin/toggle/{id}` - Включить/выключить товар

## 🧪 Тестирование

```bash
# Запуск тестов (если есть)
pytest
```

## 📦 Production развертывание

### Переменные окружения (обязательно):
```bash
SECRET_KEY=<ваш_секретный_ключ>
ADMIN_PASSWORD_HASH=<хэш_пароля>
DEBUG=false
DATABASE_URL=sqlite+aiosqlite:///./products.db
```

### Docker:
```bash
docker-compose up -d
```

## 📄 Лицензия

MIT
