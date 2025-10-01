# spinify/main_bot/main.py
import asyncio
import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

from ..common.config import MAIN_BOT_TOKEN
from ..common.db import init_core, init_bot_tables
from .schedule.runner import refresh_jobs

# Routers
from .menu import router as menu_router
from .inline import router as inline_router
from .setup import router as setup_router


def _make_bot() -> Bot:
    """
    aiogram 3.7-compatible Bot factory.
    NOTE: AiohttpSession here does not accept a 'connector=' kwarg in 3.7,
    so any IPv4/IPv6 preference should be handled at the OS level.
    """
    session = AiohttpSession(timeout=aiohttp.ClientTimeout(total=30))
    return Bot(
        MAIN_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )


async def main():
    # DB bootstrap (idempotent)
    init_core()
    init_bot_tables()

    bot = _make_bot()
    dp = Dispatcher()

    # Include routers
    dp.include_router(menu_router)
    dp.include_router(inline_router)
    dp.include_router(setup_router)

    # Start scheduler jobs (3h ON / 1h OFF, plus window checks)
    refresh_jobs()

    # Polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
