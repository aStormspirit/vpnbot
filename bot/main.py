import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from datetime import datetime
from worker import celery

from dotenv import load_dotenv
import os

from database import db
from celery.result import AsyncResult


load_dotenv()

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота и диспетчера
logging.basicConfig(level=logging.INFO)
bot = Bot(
    token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ==================== КЛАВИАТУРА ====================
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Купить VPN", callback_data="buy_vpn"),
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        ],
        [
            InlineKeyboardButton(text="📋 Правила", callback_data="rules"),
            InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
        ],
    ]
)

back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ]
)

help_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💬 Чат поддержки", callback_data="chat")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")],
    ]
)

buy_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Proxy", callback_data="proxy")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")],
    ]
)

# ==================== ТЕКСТ ====================
GREETING_TEXT = (
    "👋 <b>Добро пожаловать в AuronVPN</b>\n\n"
    "Это бот, который поможет вам легко подключиться к VPN с использованием протокола VLESS"
)

RULES_TEXT = (
    "📋 <b>Правила использования</b>\n\n"
    "Пользуясь нашим VPN - вы автоматически соглашаетесь с данными правилами использования:\n\n"
    "1. Запрещено использовать любые торрент-клиенты.\n"
    "2. Запрещено заниматься действиями, которые нарушают законы вашей страны.\n"
    "3. Запрещено заниматься действиями, которые нарушает законы той страны, локацию которой вы выбрали.\n"
    "4. Запрещено заниматься перепродажей конфигов/ключей.\n"
    "5. Возврат средств осуществляется только в течении 1-го дня действия подписки.\n\n"
    "❗️ Если вы не согласны с данным правилами, то вы вправе не пользоваться нашим VPN."
)

HELPERS_TEXT = (
    "<b>❓ Помощь</b>\n\n"
    "Прежде чем писать в поддержку, изучите базу знаний (https://myvless.com), "
    "если вашей проблемы там нет или у вас просто есть вопрос - обращайтесь в поддержку."
)

BUY_TEXT = "<b>💳 Выберите услугу</b>\n\n" "Доступные варианты для покупки:"


def format_profile_text(user_data: dict) -> str:
    """Форматирование текста профиля"""
    user_id = user_data["user_id"]
    username = (
        f"@{user_data['username']}" if user_data["username"] else "Не указан"
    )
    first_name = user_data["first_name"] or "Не указано"
    created_at = datetime.fromisoformat(user_data["created_at"]).strftime(
        "%d.%m.%Y %H:%M"
    )

    # Проверка подписки
    if user_data["subscription_end"]:
        sub_end = datetime.fromisoformat(user_data["subscription_end"])
        if sub_end > datetime.now():
            subscription_status = (
                f"✅ Активна до {sub_end.strftime('%d.%m.%Y %H:%M')}"
            )
        else:
            subscription_status = "❌ Истекла"
    else:
        subscription_status = "❌ Не активна"

    # Форматирование трафика
    traffic_gb = (
        user_data["total_traffic"] / (1024**3)
        if user_data["total_traffic"]
        else 0
    )

    return (
        f"👤 <b>Ваш профиль</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"👤 Имя: {first_name}\n"
        f"📱 Username: {username}\n"
        f"📅 Регистрация: {created_at}\n\n"
        f"📊 <b>Подписка:</b> {subscription_status}\n"
        f"📈 <b>Использовано трафика:</b> {traffic_gb:.2f} ГБ"
    )


# ==================== MIDDLEWARE ДЛЯ ОТСЛЕЖИВАНИЯ АКТИВНОСТИ ====================
@dp.message.middleware()
async def track_user_activity(handler, event: types.Message, data: dict):
    """Middleware для отслеживания активности пользователей"""
    user = event.from_user

    # Проверяем, новый ли пользователь
    is_new = await db.is_new_user(user.id)

    # Добавляем/обновляем пользователя
    await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    # Обновляем время последней активности
    await db.update_last_active(user.id)

    return await handler(event, data)


@dp.callback_query.middleware()
async def track_callback_activity(
    handler, event: types.CallbackQuery, data: dict
):
    """Middleware для отслеживания активности через callback"""
    user = event.from_user
    await db.update_last_active(user.id)
    return await handler(event, data)


# ==================== ОБРАБОТЧИК КОМАНДЫ /START ====================
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(GREETING_TEXT, reply_markup=keyboard)


# ==================== ОБРАБОТЧИКИ КНОПОК ====================
@dp.callback_query(F.data == "profile")
async def show_profile(callback: types.CallbackQuery):
    user_data = await db.get_user(callback.from_user.id)

    if user_data:
        profile_text = format_profile_text(user_data)
        await callback.message.edit_text(
            profile_text, reply_markup=back_keyboard
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка загрузки профиля. Попробуйте позже.",
            reply_markup=back_keyboard,
        )

    await callback.answer()


@dp.callback_query(F.data == "rules")
async def rules(callback: types.CallbackQuery):
    await callback.message.edit_text(RULES_TEXT, reply_markup=back_keyboard)
    await callback.answer()


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(GREETING_TEXT, reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data == "buy_vpn")
async def buy_vpn(callback: types.CallbackQuery):
    await callback.message.edit_text(BUY_TEXT, reply_markup=buy_keyboard)
    await callback.answer()


@dp.callback_query(F.data == "help")
async def help_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(HELPERS_TEXT, reply_markup=help_keyboard)
    await callback.answer()


@dp.callback_query(F.data == "chat")
async def chat_support(callback: types.CallbackQuery):
    await callback.answer(
        "Напишите в поддержку: @support_username", show_alert=True
    )

@dp.callback_query(F.data == "proxy")
async def chat_support(callback: types.CallbackQuery):
    await callback.answer("⏳ Создание прокси... Пожалуйста, подождите...", show_alert=False)
    result = celery.send_task("app.tasks.create_proxy_credentials")
    proxy = result.get(timeout=30)
    await callback.message.answer(
        "✅ <b>Прокси успешно создан!</b>\n\n" +
        f"http://{proxy['login']}:{proxy['password']}@151.241.226.127:3182\n"
    )



# ==================== КОМАНДА ДЛЯ СТАТИСТИКИ (для админа) ====================
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    # Здесь можно добавить проверку на админа
    total_users = await db.get_user_count()
    active_subs = await db.get_active_subscriptions_count()

    stats_text = (
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"✅ Активных подписок: {active_subs}"
    )

    await message.answer(stats_text)


# ==================== ЗАПУСК БОТА ====================
async def on_startup():
    """Выполняется при запуске бота"""
    logging.info("Инициализация базы данных...")
    await db.init_db()
    logging.info("База данных готова")


async def main():
    logging.info("Бот запускается...")
    await on_startup()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
