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


# /stats
async def render_handler(message: Message, swag):
    chat_id = message.chat.id
    pool = swag
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT username, swag_count FROM swagtable WHERE chat_id={chat_id} ORDER BY swag_count DESC LIMIT 10")
            rows = await cur.fetchall()
        if not rows:
            await message.answer("Еще никто не играл!")
            return
        usernames = [row[0] for row in rows]
        scores = [max(row[1], 0) for row in rows]
        if sum(scores) == 0:
            await message.answer("У всех сваг 0 или отрицательный, диаграмму не построить!")
            return
        short_names = [
            f"{score} Сваги - {(name[:20] + '…') if len(name) > 20 else name}"
            for name, score in zip(usernames, scores)
        ]

        fig = plt.figure(figsize=(14, 7))
        gs = fig.add_gridspec(1, 2, width_ratios=[1, 1])
        ax = fig.add_subplot(gs[0])
        ax_legend = fig.add_subplot(gs[1])
        ax_legend.axis('off')

        colors = ['#FF6B6B', '#FF9F43', '#FECA57', '#48DBFB', '#1DD1A1',
                  '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#C8D6E5']
        ax.set_title("TOP SWAG")
        fig.patch.set_alpha(0.5)
        wedges, texts, autotexts = ax.pie(scores, labels=None, autopct='%1.1f%%', startangle=140, pctdistance=0.85,
                                          wedgeprops=dict(width=0.6), colors=colors)
        ax_legend.legend(wedges, short_names, loc="center left", fontsize=14, frameon=True, borderpad=1)
        from PIL import Image
        import numpy as np
        from matplotlib.offsetbox import OffsetImage, AnnotationBbox

        wm = Image.open("watermark.jpg").convert("RGBA")
        wm = wm.resize((150, 150))

        mask = Image.new("L", wm.size, 0)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, wm.size[0], wm.size[1]), fill=255)
        wm.putalpha(mask)
        imagebox = OffsetImage(np.array(wm), zoom=1.0)
        ab = AnnotationBbox(imagebox, (0, 0), frameon=False)
        ax.add_artist(ab)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
        buf.seek(0)
        plt.close()
        await message.answer_photo(BufferedInputFile(buf.read(), filename='stats.png'))
