from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from states import Booking
from config import ALL_SLOTS
import db

router = Router()

# Хэндлер нажатия кнопки
@router.callback_query(F.data == "book")
async def process_booking(callback_query: types.CallbackQuery):
    calendar = SimpleCalendar()
    await callback_query.message.answer("Выбери дату:", reply_markup=await calendar.start_calendar())

# Обработка выбора даты
@router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback_query: types.CallbackQuery, callback_data: SimpleCalendarCallback):
    selected, data = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        booked_times = db.get_booked_times(str(data.date()))
        free_slots = [slot for slot in ALL_SLOTS if slot not in booked_times]

        if not free_slots:
            await callback_query.message.answer(f"❌ На {data.strftime('%Y-%m-%d')} все слоты заняты.")
            return

        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=slot, callback_data=f"time_{data.strftime('%Y-%m-%d')}_{slot}")]
                for slot in free_slots
            ]
        )
        await callback_query.message.answer(f"🗓️ Вы выбрали дату {data.strftime('%Y-%m-%d')}. Доступные слоты:", reply_markup=kb)

# Обработка выбора времени
@router.callback_query(F.data.startswith("time_"))
async def process_time(callback_query: types.CallbackQuery, state: FSMContext):
    _, chosen_date, chosen_time = callback_query.data.split("_")
    await state.update_data(date=chosen_date, time=chosen_time)
    await callback_query.message.answer(f"🗓️ Вы выбрали {chosen_date} в {chosen_time}. Теперь введите ваше имя:")
    await state.set_state(Booking.waiting_for_name)

# Имя
@router.message(Booking.waiting_for_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Спасибо! Теперь введите ваш номер телефона:")
    await state.set_state(Booking.waiting_for_phone)

# Телефон и подтверждение
@router.message(Booking.waiting_for_phone)
async def get_phone(message: types.Message, state: FSMContext):
    user_data = await state.update_data(phone=message.text)

    date_str = user_data["date"]
    if hasattr(date_str, "strftime"):
        date_str = date_str.strftime("%Y-%m-%d")

    # Запись в базу
    db.add_booking(date_str, user_data["time"], user_data["name"], user_data["phone"])

    await message.answer(
        f"✅ Бронь подтверждена!\n"
        f"Дата: {date_str}\n"
        f"Время: {user_data['time']}\n"
        f"Имя: {user_data['name']}\n"
        f"Телефон: {user_data['phone']}\n"
        f"Ожидаем вас у нас! 😉"
    )
    await state.clear()
