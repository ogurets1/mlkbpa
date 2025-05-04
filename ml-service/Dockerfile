FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Копируем ВСЕ файлы проекта
COPY . .

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /app/uploads /app/results /app/models

CMD ["sh", "scripts/start.sh"]