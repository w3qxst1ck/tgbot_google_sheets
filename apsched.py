from aiogram import Bot
from google_sheets_api import gs
from config import ADMINS


async def send_balance_report(bot: Bot):
    """Получение баланса раз в день"""
    balance = gs.get_balance()
    await bot.send_message(ADMINS[0], f"Ваш текущий баланс {balance} рублей.")