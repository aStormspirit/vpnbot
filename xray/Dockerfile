FROM alpine:latest

# Установка необходимых пакетов
RUN apk add --no-cache \
    curl \
    unzip \
    ca-certificates \
    openssl

# Скачивание и установка Xray
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then ARCH="64"; \
    elif [ "$ARCH" = "aarch64" ]; then ARCH="arm64-v8a"; \
    fi && \
    curl -L -o /tmp/xray.zip "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-${ARCH}.zip" && \
    unzip /tmp/xray.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/xray && \
    rm /tmp/xray.zip

# Создание директории для конфигурации
RUN mkdir -p /etc/xray

# Копирование конфигурационного файла
COPY config.json /etc/xray/config.json

# Копирование скрипта запуска
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Открытие портов
EXPOSE 443

ENTRYPOINT ["/entrypoint.sh"]
