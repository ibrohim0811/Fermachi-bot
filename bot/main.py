import os
import sys
import django


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
django.setup()

import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram import types

from bot.buttons import main_menu
from handlers.cow import dp as cow
from handlers.cowpdf import dp as cowpdf

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

admins = [195066733, 5020646658, 45874855, 938736625]

@dp.message(Command('start'))
async def command_start_handler(msg: types.Message):
    await msg.answer(f"Assalomu alaykum {msg.from_user.first_name} Fermachi Botiga xush kelibsiz")
    await msg.answer("⌛️")
    if msg.from_user.id in admins:
        await msg.delete()
        await msg.answer("Yana bir bor xush kelibsiz Admin 👋", reply_markup=main_menu()) #menu button
    else:
        await msg.answer("Siz admin emassiz!")
        return


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp.include_router(cow)
    dp.include_router(cowpdf)
    await dp.start_polling(bot)


if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)

    asyncio.run(main()) 