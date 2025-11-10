import secrets
import string
import logging
import os
from typing import Dict


logger = logging.getLogger(__name__)

# Настройки прокси-сервера из переменных окружения
PROXY_HOST = os.getenv("PROXY_HOST", "your-server-ip")
PROXY_SOCKS_PORT = os.getenv("PROXY_SOCKS_PORT", "1080")
PROXY_HTTP_PORT = os.getenv("PROXY_HTTP_PORT", "3128")


class ProxyManager:
    """Класс для управления прокси"""
    
    @staticmethod
    def generate_credentials() -> Dict[str, str]:
        """
        Генерация логина и пароля для прокси
        
        Returns:
            Dict с полями login и password
        """
        # Генерируем случайный логин (8 символов)
        login = 'user_' + ''.join(
            secrets.choice(string.ascii_lowercase + string.digits) 
            for _ in range(8)
        )
        
        # Генерируем случайный пароль (16 символов)
        password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + string.punctuation) 
            for _ in range(16)
        )
        
        logger.info(f"Сгенерированы credentials: {login}")
        
        return {
            "login": login,
            "password": password
        }

    @staticmethod
    async def create_proxy_user(login: str, password: str, passwd_file: str = "/etc/3proxy/passwd") -> bool:
        """
        Создание пользователя прокси в файле паролей 3proxy
        
        Args:
            login: Логин пользователя
            password: Пароль пользователя
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            # Путь к файлу паролей 3proxy
            passwd_file = passwd_file
            
            # Формируем строку в формате 3proxy: login:CL:password
            user_line = f"{login}:CL:{password}\n"
            
            # Проверяем существование файла
            if not os.path.exists(passwd_file):
                logger.warning(f"Файл {passwd_file} не найден. Создаем новый.")
                os.makedirs(os.path.dirname(passwd_file), exist_ok=True)
            
            # Проверяем, не существует ли уже такой пользователь
            if os.path.exists(passwd_file):
                with open(passwd_file, 'r') as f:
                    if any(line.startswith(f"{login}:") for line in f):
                        logger.warning(f"Пользователь {login} уже существует")
                        return False
            
            # Добавляем пользователя в файл
            with open(passwd_file, 'a') as f:
                f.write(user_line)
            
            logger.info(f"Пользователь {login} добавлен в прокси")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания пользователя прокси: {e}")
            return False

    @staticmethod
    async def reload_proxy_config() -> bool:
        """
        Перезагрузка конфигурации 3proxy
        
        Returns:
            True если успешно, False если ошибка
        """
        try:
            import subprocess
            
            result = subprocess.run(
                ["pkill", "-HUP", "3proxy"],
                capture_output=True,
                text=True
            )
            
            if kill.returncode == 0:
                logger.info("Конфигурация 3proxy перезагружена")
                return True
            else:
                logger.warning(f"Не удалось перезагрузить 3proxy: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка перезагрузки прокси: {e}")
            return False
