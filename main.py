import aiogram
from aiogram import Dispatcher, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery
from random import randint, choice
import aiomysql
from datetime import datetime, timedelta

TokenApi = '8459518598:AAENhrVn8sUrcShd_1lFbV3_Sb3cJJ9H-ks'

bot = Bot(token=TokenApi)
dp = Dispatcher()

# /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎲 СвагоМетр", callback_data="swag")]])
    await message.answer("Привет! Используй /swag, чтобы стать крутым😎", reply_markup=keyboard)


# /help
@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer("Команды: \n/swag\n/start\n/help\n/test")

# /test
@dp.message(Command("test"))
async def test_handler(message: Message):
    await message.answer("Работает ✅")

@dp.callback_query(F.data == "swag")
async def swag_handler(message: Message, swag):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    rand = randint(-10,10)
    pool = swag
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT * FROM swagtable where id_user={user_id}")
            row = await cur.fetchone()
            if row is not None:
                last_used = row[3]
                if last_used and datetime.now() - last_used < timedelta(hours=1):
                    remaining = timedelta(hours=1) - (datetime.now() - last_used)
                    minutes = int(remaining.total_seconds() // 60)
                    seconds = int(remaining.total_seconds() % 60)
                    await message.answer(f"{username}, ⏳ Подожди ещё {minutes} минут\n Текущий сваг: {row[2]}")
                    return
            if row is None:
                await cur.execute(
                    f"insert into swagtable (id_user, username, swag_count, last_used) values ({user_id}, '{username}', {rand}, NOW())",
                )
                current = rand
            else:
                text = f"{username}, "
                current = row[2] + rand
                await cur.execute(f"update swagtable set swag_count={current}, last_used=NOW() where id_user={user_id}")
            if (rand > 0):
                text += choice([f"🔥 Жестко! +{rand} к свагу",
                               f"📈 Ты на подъёме: +{rand}",
                               f"💪 Сваг прокачался на {rand}",
                               f"😱 Не, ну это прайм! +{rand} к свагу "
                              ])
            elif (rand < 0):
                text += choice([f"📉 Просадка.. -{abs(rand)}",
                               f"Сваг просел на {abs(rand)} 😬",
                               f"💀 Минус {abs(rand)} сваги к уверенности"
                               ])
            if (rand == 0):
                text = f"🥶 Сваг без изменений.."

            text += f"\nТекущий сваг: {current}"
            await message.answer(text)


@dp.message(Command("swag"))
async def swag_handler(message: Message, swag):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    rand = randint(-10,10)
    pool = swag
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT * FROM swagtable where id_user={user_id}")
            row = await cur.fetchone()
            if row is not None:
                last_used = row[3]
                if last_used and datetime.now() - last_used < timedelta(hours=1):
                    remaining = timedelta(hours=1) - (datetime.now() - last_used)
                    minutes = int(remaining.total_seconds() // 60)
                    seconds = int(remaining.total_seconds() % 60)
                    await message.answer(f"{username}, ⏳ Подожди ещё {minutes} минут\n Текущий сваг: {row[2]}")
                    return
            if row is None:
                await cur.execute(
                    f"insert into swagtable (id_user, username, swag_count, last_used) values ({user_id}, '{username}', {rand}, NOW())",
                )
                current = rand
            else:
                text = f"{username}, "
                current = row[2] + rand
                await cur.execute(f"update swagtable set swag_count={current}, last_used=NOW() where id_user={user_id}")
            if (rand > 0):
                text += choice([f"🔥 Жестко! +{rand} к свагу",
                               f"📈 Ты на подъёме: +{rand}",
                               f"💪 Сваг прокачался на {rand}",
                               f"😱 Не, ну это прайм! +{rand} к свагу "
                              ])
            elif (rand < 0):
                text += choice([f"📉 Просадка.. -{abs(rand)}",
                               f"Сваг просел на {abs(rand)} 😬",
                               f"💀 Минус {abs(rand)} сваги к уверенности"
                               ])
            if (rand == 0):
                text = f"🥶 Сваг без изменений.."

            text += f"\nТекущий сваг: {current}"
            await message.answer(text)

@dp.message()
async def message_handler(message: Message):
    if message.from_user.id == 6008947194:
        await message.answer("Мурик не выёбывайся")


async def main():
  async def main():
    import os
    pool = await aiomysql.create_pool(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        db=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306)),
        autocommit=True, minsize=1, maxsize=5
    )
    print("бот запущен")
    await dp.start_polling(bot, swag=pool)


if __name__ == '__main__':
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
