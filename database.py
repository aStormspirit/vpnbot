import aiosqlite
import logging
from datetime import datetime
from typing import Optional, Dict, Any

DATABASE_PATH = "data/vpnbot.db"

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    subscription_end TIMESTAMP NULL,
                    total_traffic INTEGER DEFAULT 0
                )
            """)
            await db.commit()
            logger.info("База данных инициализирована")

    async def add_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> bool:
        """Добавление нового пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        username = excluded.username,
                        first_name = excluded.first_name,
                        last_name = excluded.last_name,
                        last_active = CURRENT_TIMESTAMP
                    """,
                    (user_id, username, first_name, last_name)
                )
                await db.commit()
                logger.info(f"Пользователь {user_id} добавлен/обновлен")
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя: {e}")
            return False

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение информации о пользователе"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM users WHERE user_id = ?",
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
                    return None
        except Exception as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return None

    async def update_last_active(self, user_id: int):
        """Обновление времени последней активности"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_id,)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Ошибка обновления last_active: {e}")

    async def get_user_count(self) -> int:
        """Получение общего количества пользователей"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result else 0
        except Exception as e:
            logger.error(f"Ошибка получения количества пользователей: {e}")
            return 0

    async def is_new_user(self, user_id: int) -> bool:
        """Проверка, является ли пользователь новым"""
        user = await self.get_user(user_id)
        return user is None

    async def update_subscription(self, user_id: int, end_date: datetime):
        """Обновление даты окончания подписки"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE users SET subscription_end = ? WHERE user_id = ?",
                    (end_date, user_id)
                )
                await db.commit()
                logger.info(f"Подписка пользователя {user_id} обновлена")
        except Exception as e:
            logger.error(f"Ошибка обновления подписки: {e}")

    async def get_active_subscriptions_count(self) -> int:
        """Получение количества активных подписок"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    """
                    SELECT COUNT(*) FROM users 
                    WHERE subscription_end IS NOT NULL 
                    AND subscription_end > CURRENT_TIMESTAMP
                    """
                ) as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result else 0
        except Exception as e:
            logger.error(f"Ошибка получения активных подписок: {e}")
            return 0


# Создаем глобальный экземпляр базы данных
db = Database()