from aiogram.fsm.state import StatesGroup, State

# Определение состояния
class Booking(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()