FROM python:3.13-slim

WORKDIR /app

# Установка зависимостей системы
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Копирование файлов проекта
COPY pyproject.toml uv.lock ./

# Установка зависимостей
RUN uv sync --frozen --no-dev

# Копирование остального кода
COPY . .

# Создание директории для статики
RUN mkdir -p static/uploads/products

# Переменная окружения для базы данных (можно переопределить в docker-compose)
ENV DATABASE_URL=sqlite:///./data/products.db

# Создание директории для данных
RUN mkdir -p data

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
