FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы конфигурации poetry
COPY pyproject.toml poetry.lock* ./

# Настраиваем poetry (не создавать виртуальное окружение)
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости
RUN poetry install --no-interaction --no-ansi --no-root --only main

# Копируем все файлы проекта
COPY . .

# Запускаем бота
CMD ["python", "main.py"]