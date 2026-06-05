from aiogram import types, Router
from aiogram.filters import Command
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

import db

router = Router()
ADMIN_ID = 847895304

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к админ‑панели.")
        return

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="📋 Все заявки", callback_data="admin_view_all")],
            [types.InlineKeyboardButton(text="📅 Заявки на дату", callback_data="admin_view_date")],
            [types.InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
            [types.InlineKeyboardButton(text="🗑 Очистить базу", callback_data="admin_clear")]
        ]
    )
    await message.answer("⚙️ Админ‑панель:", reply_markup=kb)


@router.callback_query(lambda c: c.data == "admin_view_all")
async def admin_view_all(callback_query: types.CallbackQuery):
    rows = db.get_all_bookings()
    if not rows:
        await callback_query.message.answer("📭 Пока нет заявок.")
        return

    text = "📋 Все заявки:\n\n"
    grouped = {}
    for date, time, name, phone in rows:
        grouped.setdefault(date, []).append((time, name, phone))

    for date, bookings in grouped.items():
        text += f"📅 {date}\n"
        for time, name, phone in sorted(bookings):
            text += f"- {time} {name} ({phone})\n"
        text += "\n"

    await callback_query.message.answer(text)

# Заявки через календарь
@router.callback_query(lambda c: c.data == "admin_view_date")
async def admin_view_date(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Введите дату в формате YYYY-MM-DD:")


@router.message(lambda m: m.text and m.text.count("-") == 2)
async def show_bookings_by_date(message: types.Message):
    rows = db.get_bookings_by_date(message.text.strip())
    if not rows:
        await message.answer(f"📭 На {message.text} заявок нет.")
        return

    text = f"📋 Заявки на {message.text}:\n\n"
    for time, name, phone in rows:
        text += f"- {time} {name} ({phone})\n"
    await message.answer(text)


# Статистика
@router.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback_query: types.CallbackQuery):
    rows = db.get_all_bookings()
    if not rows:
        await callback_query.message.answer("📭 Пока нет заявок.")
        return

    # Считаем количевство заявок по датам
    stats_by_date = {}
    stats_by_time = {}
    for date, time, name, phone in rows:
        stats_by_date[date] = stats_by_date.get(date, 0) + 1
        stats_by_time[time] = stats_by_time.get(time, 0) + 1

    text = "📊 Статистика:\n\n"
    text += "📅 Заявки по датам:\n"
    for date, count in stats_by_date.items():
        text += f"- {date}: {count}\n"

    text += "\n⏰ Популярные слоты:\n"
    for time, count in sorted(stats_by_time.items(), key=lambda x: x[1], reverse=True):
        text += f"- {time}: {count}\n"

    await callback_query.message.answer(text)


@router.callback_query(lambda c: c.data == "admin_clear")
async def admin_clear(callback_query: types.CallbackQuery):
    db.clear_bookings()
    await callback_query.message.answer("🗑 Все заявки удалены.")
