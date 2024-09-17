from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def operations_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура действий"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Получил ➕", callback_data=f"operation_plus"))
    keyboard.row(InlineKeyboardButton(text="Потратил ➖", callback_data=f"operation_minus"))
    keyboard.row(InlineKeyboardButton(text="Пополнить баланс 💰", callback_data=f"add_balance"))
    keyboard.adjust(2)
    return keyboard


def cancel_keyboard() -> InlineKeyboardBuilder:
    """Keyboard with cancel button"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Отмена", callback_data=f"cancel"))
    return keyboard