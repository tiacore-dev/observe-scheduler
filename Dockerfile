# ===== Этап 1: билд зависимостей =====
FROM python:3.12-slim AS builder

WORKDIR /app

# Устанавливаем зависимости для сборки Python-пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt

# ===== Этап 2: прод-окружение без мусора =====
FROM python:3.12-slim

WORKDIR /app

# Копируем готовые зависимости
COPY --from=builder /install /usr/local

# Копируем исходный код
COPY . .

# Команда по умолчанию
CMD ["python", "main.py"]
