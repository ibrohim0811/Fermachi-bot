from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton



def main_menu() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Sut 🥛", callback_data="milk"),
                InlineKeyboardButton(text="Yangilik 🐄", callback_data="new")
            ],
            [
                InlineKeyboardButton(text="Sut Hisobot 🗒", callback_data="milkpdf"),
                InlineKeyboardButton(text="Buzoq Hisobot 🗒", callback_data="cowpdf")
            ]
        ]
    )

def auto_time():

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Vaqtni avtomatik kiritish 🕔")]
        ]
    )

