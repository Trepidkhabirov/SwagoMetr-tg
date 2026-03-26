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

TokenApi = os.getenv("TOKEN_API")

bot = Bot(token=TokenApi)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎲 СвагоМетр", callback_data="swag")]])
    await message.answer("Привет! Используй /swag, чтобы стать крутым😎", reply_markup=keyboard)

@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer("Команды: \n/swag\n/start\n/help\n/test")

@dp.message(Command("test"))
async def test_handler(message: Message):
    await message.answer("Работает ✅")

@dp.callback_query(F.data == "swag")
async def swag_callback(callback: CallbackQuery, swag):
    user_id = callback.from_user.id
    username = callback.message.from_user.full_name
    chat_id = callback.message.chat.id
    rand = randint(-10, 10)
    pool = swag
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT * FROM swagtable where id_user={user_id} and chat_id={chat_id}")
            row = await cur.fetchone()
            if row is not None:
                last_used = row[3]
                if last_used and datetime.now() - last_used < timedelta(hours=1):
                    remaining = timedelta(hours=1) - (datetime.now() - last_used)
                    minutes = int(remaining.total_seconds() // 60)
                    await callback.message.answer(f"{username}, ⏳ Подожди ещё {minutes} минут\n Текущий сваг: {row[2]}")
                    await callback.answer()
                    return
            if row is None:
                await cur.execute(f"insert into swagtable (id_user, username, swag_count, last_used, chat_id) values ({user_id}, '{username}', {rand}, NOW(), {chat_id})")
                current = rand
            else:
                current = row[2] + rand
                await cur.execute(f"update swagtable set swag_count={current}, last_used=NOW() where id_user={user_id} and chat_id = {chat_id}")
            text = f"{username}, "
            if rand > 0:
                text += choice([f"🔥 Жестко! +{rand} к свагу", f"📈 Ты на подъёме: +{rand}", f"💪 Сваг прокачался на {rand}", f"😱 Не, ну это прайм! +{rand} к свагу"])
            elif rand < 0:
                text += choice([f"📉 Просадка.. -{abs(rand)}", f"Сваг просел на {abs(rand)} 😬", f"💀 Минус {abs(rand)} сваги к уверенности"])
            else:
                text = f"🥶 Сваг без изменений.."
            text += f"\nТекущий сваг: {current}"
            await callback.message.answer(text)
            await callback.answer()

@dp.message(Command("swag"))
async def swag_handler(message: Message, swag):
    user_id = message.from_user.id
    username = message.from_user.full_name
    rand = randint(-10, 10)
    chat_id = message.chat.id
    pool = swag
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT * FROM swagtable where id_user={user_id} and chat_id = {chat_id}")
            row = await cur.fetchone()
            if row is not None:
                last_used = row[3]
                if last_used and datetime.now() - last_used < timedelta(hours=1):
                    remaining = timedelta(hours=1) - (datetime.now() - last_used)
                    minutes = int(remaining.total_seconds() // 60)
                    await message.answer(f"{username}, ⏳ Подожди ещё {minutes} минут\n Текущий сваг: {row[2]}")
                    return
            if row is None:
                await cur.execute(f"insert into swagtable (id_user, username, swag_count, last_used, chat_id) values ({user_id}, '{username}', {rand}, NOW(), {chat_id})")
                current = rand
            else:
                current = row[2] + rand
                await cur.execute(f"update swagtable set swag_count={current}, last_used=NOW() where id_user={user_id} and chat_id = {chat_id}")
            text = f"{username}, "
            if rand > 0:
                text += choice([f"🔥 Жестко! +{rand} к свагу", f"📈 Ты на подъёме: +{rand}", f"💪 Сваг прокачался на {rand}", f"😱 Не, ну это прайм! +{rand} к свагу"])
            elif rand < 0:
                text += choice([f"📉 Просадка.. -{abs(rand)}", f"Сваг просел на {abs(rand)} 😬", f"💀 Минус {abs(rand)} сваги к уверенности"])
            else:
                text = f"🥶 Сваг без изменений.."
            text += f"\nТекущий сваг: {current}"
            await message.answer(text)

from stats import stats_handler
# /stats
@dp.message(Command("stats"))
async def stats_handler(message: Message, swag):
    await stats_handler(message, swag)

from statstext import stats_handler
# /top
@dp.message(Command("top"))
async def top_handler(message: Message, swag):
    await stats_handler(message, swag)


@dp.message()
async def message_handler(message: Message):
    if message.from_user.id == 6008947194:
        await message.answer("Мурик не выёбывайся")

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
