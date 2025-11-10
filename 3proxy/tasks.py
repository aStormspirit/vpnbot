import asyncio
import logging
import os

from celery import Celery
from .proxymanager import ProxyManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("3proxy")

# Настройка Celery
CELERY_BROKER_URL = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379"
)
CELERY_RESULT_BACKEND = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379"
)

celery_app = Celery(
    "3proxy", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_default_retry_delay=60,
    task_max_retries=3,
)

proxymanager = ProxyManager()


@celery_app.task(bind=True)
def create_proxy_credentials(
    self,
) -> None:
    """Создание учетных данных для прокси"""
    # Генерируем учетные данные
    credentials = proxymanager.generate_credentials()
    
    # Выполняем асинхронные операции в синхронном контексте
    async def _create_and_reload():
        await proxymanager.create_proxy_user(
            credentials["login"], 
            credentials["password"]
        )
        await proxymanager.reload_proxy_config()
    
    # Запускаем асинхронный код
    asyncio.run(_create_and_reload())

    return {
            "status": "success",
            "login": credentials["login"],
            "password": credentials["password"]
        }
