# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Синхронизируем зависимости через uv
RUN uv sync --frozen --no-dev

# Копируем исходный код
COPY src/ ./src/
COPY data/ ./data/
COPY .env ./
COPY search_index.json ./

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash appuser && \
  chown -R appuser:appuser /app

USER appuser

# Указываем команду для запуска (замените на вашу)
CMD ["python", "-m", "src.main"]
