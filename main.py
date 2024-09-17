import asyncio
from datetime import datetime
from asyncio.log import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import apsched

import aiogram as io
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from config import BOT_TOKEN
import admin
import users

#
# async def set_commands(bot: io.Bot):
#     """Перечень команд для бота"""
#     commands = [
#         BotCommand(command="start", description="Запуск бота"),
#         BotCommand(command="balance", description="Пополнить баланс"),
#     ]
#
#     await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot() -> None:
    """Запуск бота"""
    bot = io.Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # await set_commands(bot)

    storage = MemoryStorage()
    dispatcher = io.Dispatcher(storage=storage)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(apsched.send_balance_report, trigger="cron", year='*', month='*', day="*", hour=21,
                      minute=0, second=0, start_date=datetime.now(), kwargs={"bot": bot})
    scheduler.start()

    dispatcher.include_routers(admin.router, users.router)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logger.info("Запуск бота...")
    asyncio.run(start_bot())
