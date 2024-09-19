from aiogram import Bot
from google_sheets_api import gs
from config import ADMINS


async def send_balance_report(bot: Bot):
    """Получение баланса раз в день"""
    msg = "⚠️ <i>Ежедневный отчет:</i>\n\n"

    balance_info = gs.get_all_info_from_balance()
    if not balance_info:
        msg += "Данные отсутствуют"
        await bot.send_message(ADMINS[0], msg)
        return

    for row in balance_info:
        msg += f"<b>{row[0]}.</b> Тг ID: {row[1]} пользователь <b>{row[4]} ({row[2]})</b> сумма: <b>{row[3]}</b> руб. \n\n"

    for admin in ADMINS:
        await bot.send_message(admin, msg)