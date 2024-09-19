from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def operations_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура действий"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Получил ➕", callback_data=f"operation_plus"))
    keyboard.row(InlineKeyboardButton(text="Потратил ➖", callback_data=f"operation_minus"))
    keyboard.adjust(2)
    keyboard.row(InlineKeyboardButton(text="Пополнить баланс 💰", callback_data=f"add_balance"))
    keyboard.row(InlineKeyboardButton(text="Получить отчет 📊", callback_data=f"get_report"))
    return keyboard


def all_users_keyboard(all_tg_id: list, all_username: list) -> InlineKeyboardBuilder:
    """Клавиатура выбора пользователя для пополнения"""
    keyboard = InlineKeyboardBuilder()
    for i in range(len(all_tg_id)):
        keyboard.row(InlineKeyboardButton(text=f"{all_username[i]}", callback_data=f"add!@#$%{all_tg_id[i]}!@#$%{all_username[i]}"))
    keyboard.adjust(2)
    keyboard.row(InlineKeyboardButton(text="Отмена", callback_data=f"cancel"))
    return keyboard


def cancel_keyboard() -> InlineKeyboardBuilder:
    """Keyboard with cancel button"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Отмена", callback_data=f"cancel"))
    return keyboard
