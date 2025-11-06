FROM ubuntu:22.04

# Установка необходимых пакетов
RUN apt-get update && \
    apt-get install -y wget python3 python3-pip procps && \
    wget https://github.com/z3APA3A/3proxy/releases/download/0.9.4/3proxy-0.9.4.x86_64.deb && \
    dpkg -i 3proxy-0.9.4.x86_64.deb || apt-get install -f -y && \
    mkdir -p /etc/3proxy /var/log/3proxy /app && \
    rm -f 3proxy-0.9.4.x86_64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копирование конфигурационных файлов
COPY 3proxy.cfg /etc/3proxy/3proxy.cfg
COPY passwd /etc/3proxy/passwd

RUN chmod 600 /etc/3proxy/passwd

# Установка Python зависимостей
COPY tasks.py /app/tasks.py
COPY proxymanager.py /app/proxymanager.py
RUN pip3 install celery redis

# Копирование и настройка entrypoint скрипта
COPY init.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 1080 3128

ENTRYPOINT ["/app/entrypoint.sh"]
