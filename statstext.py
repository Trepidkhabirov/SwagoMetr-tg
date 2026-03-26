import aiogram
from aiogram import Dispatcher, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, BufferedInputFile
from random import randint, choice
import aiomysql
from matplotlib import font_manager
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io

async def stats_text_handler(message: Message, swag):
    chat_id = message.chat.id
    async with swag.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SELECT username, swag_count FROM swagtable WHERE chat_id={chat_id} ORDER BY swag_count DESC LIMIT 5")
            rows = await cur.fetchall()
    if not rows:
        await message.answer("Еще никто не играл!")
        return

    text = "🏆 Топ свагеров:\n\n"
    for i, (name, score) in enumerate(rows, 1):
        text += f"{i}. {score} Сваги — {name}\n"
    await message.answer(text)