#!/bin/bash
# Скрипт для запуска сервера куриц-гриль

cd "$(dirname "$0")"

echo "🍗 Запускаем сервер Курица-Гриль..."
echo "📍 Адрес: http://localhost:8000"
echo "🔐 Админка: http://localhost:8000/admin"
echo "   Логин: admin"
echo "   Пароль: admin123"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo ""

uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
