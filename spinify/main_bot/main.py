# spinify/main_bot/main.py
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

from ..common.config import MAIN_BOT_TOKEN
from ..common.db import init_core, init_bot_tables
from .schedule.runner import refresh_jobs

from .menu import router as menu_router
from .inline import router as inline_router
from .setup import router as setup_router

def _make_bot() -> Bot:
    # aiogram 3.7 expects "timeout" as seconds (int/float), not ClientTimeout
    session = AiohttpSession(timeout=30)
    return Bot(
        MAIN_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )

async def main():
    init_core(); init_bot_tables()

    bot = _make_bot()
    dp = Dispatcher()

    dp.include_router(menu_router)
    dp.include_router(inline_router)
    dp.include_router(setup_router)

    refresh_jobs()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
