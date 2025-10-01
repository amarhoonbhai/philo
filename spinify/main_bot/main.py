import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from ..common.config import MAIN_BOT_TOKEN
from ..common.db import init_core, init_bot_tables
from .menu import router as menu_router
from .gate import router as gate_router

async def main():
    init_core(); init_bot_tables()
    bot = Bot(
        MAIN_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(gate_router)
    dp.include_router(menu_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
