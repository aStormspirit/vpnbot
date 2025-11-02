#!/bin/bash

# Скрипт для ручного деплоя на сервер
# Использование: ./deploy.sh

set -e

echo "🚀 Starting deployment..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка наличия docker и docker-compose
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

# Получаем последние изменения
echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
git pull origin main || git pull origin master

# Останавливаем текущий контейнер
echo -e "${YELLOW}🛑 Stopping current container...${NC}"
docker-compose down

# Создаем .env если его нет
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    echo -e "${YELLOW}📝 Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}❗ Please edit .env file and add your BOT_TOKEN${NC}"
    exit 1
fi

# Проверяем наличие BOT_TOKEN
if ! grep -q "BOT_TOKEN=" .env || grep -q "BOT_TOKEN=your_bot_token_here" .env; then
    echo -e "${RED}❌ BOT_TOKEN is not set in .env file${NC}"
    exit 1
fi

# Пересобираем и запускаем контейнер
echo -e "${YELLOW}🔨 Building and starting container...${NC}"
docker-compose up -d --build

# Очищаем старые образы
echo -e "${YELLOW}🧹 Cleaning up old images...${NC}"
docker image prune -f

# Ждем запуска
echo -e "${YELLOW}⏳ Waiting for container to start...${NC}"
sleep 5

# Проверяем статус
if [ "$(docker-compose ps -q vpnbot | wc -l)" -eq 0 ]; then
    echo -e "${RED}❌ Container failed to start!${NC}"
    echo -e "${YELLOW}📋 Last 50 lines of logs:${NC}"
    docker-compose logs --tail=50
    exit 1
else
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -