import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
django.setup()

from aiogram import Router, F
from aiogram import types
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext
from datetime import date

from bot.state import New
from app.models import CowBorn
from bot.buttons import main_menu

dp = Router()

def create_cowborn(name, time):
    return CowBorn.objects.create(parent=name, date=time)

@dp.callback_query(F.data == "new")
async def add_cow_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("Tug'gan sigir nomini kiriting: ")
    await state.set_state(New.parent)

@dp.message(New.parent)
async def add_time(msg: types.Message, state: FSMContext):
    name = msg.text

    await state.update_data(name=name)
    await msg.answer("Qachon tug'gan yoki tug'di vaqtni kiriting\nFormat: 2026-06-17 \n Avtomatik kiritish uchun /auto yozing.")
    await state.set_state(New.date)



@dp.message(New.date)
async def save_time(msg: types.Message, state: FSMContext):
    if msg.text == "/auto":
        time = date.today()
    else:
        time = msg.text

    await state.update_data(time=time)
    await msg.answer("Malumotlar Tayyorlanmoqda...")

    #proccess

    data = await state.get_data()
    name = data.get("name")
    time = data.get("time")
    try:
        await sync_to_async(create_cowborn)(name, time)
        await msg.answer("Saqlandi ✅")
        await msg.answer("Menudan birini tanlang: ", reply_markup=main_menu())
    except Exception as e:
        await msg.answer(f"Xatolik Yuz berdi adminga yuboring!!: \n{e}")
        print(e)





