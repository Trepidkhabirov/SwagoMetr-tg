from asyncio import start_server

import aiogram
import sys
sys.stdout.reconfigure(line_buffering=True)
from aiogram import Dispatcher, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from random import randint, choice
import aiomysql
from datetime import datetime, timedelta
import os

TokenApi = os.getenv("8769501022:AAHeVsxFvCThJZmmGVOS2PHGAoQ2tYt818U")

bot = Bot(token=TokenApi)
dp = Dispatcher()

async def main():
    pool = await aiomysql.create_pool(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        db=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306)),
        autocommit=True, minsize=1, maxsize=5
    )
    print("бот запущен", flush=True)
    await dp.start_polling(bot, swag=pool)

if __name__ == '__main__':
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
