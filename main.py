import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Настройки
BOT_TOKEN = "7700574471:AAE60UDm3-mvorrEWIt35tGoZGW4JX7roi0"

# Инициализация бота и диспетчера
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Хранилище для отслеживания новых пользователей (в памяти)
greeted_users = set()

# ==================== КЛАВИАТУРА ====================
# Создаем inline-кнопки
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Купить VPN", callback_data="buy_vpn"),
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile")
        ],
        [
            InlineKeyboardButton(text="📋 Правила", callback_data="rules"),
            InlineKeyboardButton(text="❓ Помощь", callback_data="help")
        ]
    ]
)

# Клавиатура с кнопкой "Назад"
back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ]
)

help_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Чат поддержки", callback_data="chat")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ]
)

back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Чат поддержки", callback_data="chat")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ]
)

buy_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Proxy", callback_data="chat")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
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
    "<b>Помощь</b>\n\n"
    "Прежде чем писать в поддержку, изучите базу знаний (https://myvless.com), если вашей проблемы там нет или у вас просто есть вопрос - обращайтесь в поддержку."
)

BUY_TEXT = (
    "<b>Выберите услугу</b>\n\n"
    ""
)


# ==================== ОБРАБОТЧИК КОМАНДЫ /START ====================
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    # Основное меню С КНОПКАМИ
    await message.answer(GREETING_TEXT, reply_markup=keyboard)


# ==================== ОБРАБОТЧИКИ КНОПОК ====================
@dp.callback_query(F.data == "rules")
async def rules(callback: types.CallbackQuery):
    await callback.message.edit_text(RULES_TEXT, reply_markup=back_keyboard)
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(GREETING_TEXT, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "buy_vpn")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(BUY_TEXT, reply_markup=buy_keyboard)
    await callback.answer()

@dp.callback_query(F.data == "help")
async def help(callback: types.CallbackQuery):
    await callback.message.edit_text(HELPERS_TEXT, reply_markup=help_keyboard)
    await callback.answer()

# ==================== ЗАПУСК БОТА ====================
async def main():
    logging.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())