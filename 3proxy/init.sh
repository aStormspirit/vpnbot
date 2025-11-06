#!/bin/bash
set -e

# Функция для корректного завершения
cleanup() {
    echo "Получен сигнал завершения, останавливаем 3proxy..."
    if [ -f /var/run/3proxy.pid ]; then
        kill $(cat /var/run/3proxy.pid) 2>/dev/null || true
    fi
    pkill -f "3proxy" 2>/dev/null || true
    exit 0
}

# Обработка сигналов
trap cleanup SIGTERM SIGINT

# Создаем директорию для логов если её нет
mkdir -p /var/log/3proxy

# Запуск 3proxy в фоновом режиме
echo "Запуск 3proxy..."
3proxy /etc/3proxy/3proxy.cfg &

# Сохраняем PID процесса
PROXY_PID=$!
echo $PROXY_PID > /var/run/3proxy.pid

# Ждем запуска 3proxy
sleep 2

# Проверяем, что 3proxy запущен
if ! kill -0 $PROXY_PID 2>/dev/null; then
    echo "Ошибка: 3proxy не запустился"
    cat /var/log/3proxy/*.log 2>/dev/null || true
    exit 1
fi

echo "3proxy успешно запущен (PID: $PROXY_PID)"
echo "SOCKS5 прокси доступен на порту 1080"
echo "HTTP прокси доступен на порту 3128"

# Держим контейнер запущенным и следим за процессом
while kill -0 $PROXY_PID 2>/dev/null; do
    sleep 1
done

echo "3proxy завершил работу"
exit 1

