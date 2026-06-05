from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


router = Router()

# Хэндлер команды /start
@router.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Забронировать место", callback_data="book")]
        ]
    )
    await message.answer(
        "Привет! Я бот для бронирования мест в игровом клубе. Нажми кнопку ниже:",
        reply_markup=kb
    )