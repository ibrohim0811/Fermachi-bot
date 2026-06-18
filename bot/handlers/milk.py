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

from bot.state import MilkState
from app.models import Milk
from bot.buttons import main_menu

dp = Router()

def create_cowborn(litr, time):
    return Milk.objects.create(litr=litr, date=time)



@dp.callback_query(F.data == "milk")
async def add_cow_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("Necha litr sut topshirdingiz?: ")
    await state.set_state(MilkState.litres)



@dp.message(MilkState.litres)
async def add_time(msg: types.Message, state: FSMContext):
    litr = msg.text
    if litr.isdigit():
        litr = int(litr)
    await state.update_data(litr=litr)
    await msg.answer("Sut topshirilgan vaqtni kiriting: \nFormat: 2026-06-17 \n Avtomatik kiritish uchun /auto yozing.")
    await state.set_state(MilkState.date)



@dp.message(MilkState.date)
async def save_time(msg: types.Message, state: FSMContext):
    if msg.text == "/auto":
        time = date.today()
    else:
        time = msg.text

    await state.update_data(time=time)
    await msg.answer("Malumotlar Tayyorlanmoqda...")

    #proccess

    data = await state.get_data()
    litr = data.get("litr")
    time = data.get("time")
    try:
        await sync_to_async(create_cowborn)(litr, time)
        await msg.answer("Saqlandi ✅")
        await msg.answer("Menudan birini tanlang: ", reply_markup=main_menu())
    except Exception as e:
        await msg.answer(f"Xatolik Yuz berdi adminga yuboring!!: \n{e}")
        print(e)





