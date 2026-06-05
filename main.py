from aiogram import Bot, Dispatcher
from aiogram import Router
import asyncio
from dotenv import load_dotenv
import os

from aiogram.fsm.storage.memory import MemoryStorage
from handlers import start, booking, admin

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

dp.include_router(start.router)
dp.include_router(booking.router)
dp.include_router(admin.router)



async def main():
    await dp.start_polling(bot)

print("Бот запущен!")

if __name__ == "__main__":
    asyncio.run(main())