import importlib.util
from pathlib import Path
import tempfile
import os
import pytest
from unittest.mock import Mock, patch


# Импорт модуля с именем, начинающимся с цифры
module_path = Path(__file__).parent.parent / "3proxy" / "proxymanager.py"
spec = importlib.util.spec_from_file_location("proxymanager", module_path)
proxymanager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proxymanager_module)
ProxyManager = proxymanager_module.ProxyManager

@pytest.fixture
def mock_proxy_file():
    """Фикстура для мока файла прокси"""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    yield temp_path
    
    # Очистка
    if os.path.exists(temp_path):
        os.unlink(temp_path)

class TestProxyManager:
    def test_generate_credentials(self):
        credentials = ProxyManager.generate_credentials()
        assert credentials["login"] is not None
        assert credentials["password"] is not None

    # async def test_create_proxy_user(self, mock_proxy_file):
        
    #     # Патчим путь к файлу
    #     with patch('3proxy.proxymanager.ProxyManager.passwd_file', mock_proxy_file):
    #         credentials = ProxyManager.generate_credentials()
            
    #         # Первый вызов - должен создать пользователя
    #         result1 = await ProxyManager.create_proxy_user(
    #             credentials["login"], 
    #             credentials["password"]
    #         )
    #         assert result1 is True