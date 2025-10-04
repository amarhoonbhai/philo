# spinify/main_bot/main.py
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties

from aiogram.filters import CommandStart

from ..common.config import MAIN_BOT_TOKEN
from .gate import router as gate_router

# These may exist in your project; include if present
try:
    from .menu import start as menu_start
except Exception as e:
    menu_start = None
    logging.getLogger(__name__).warning("menu.start not found: %s", e)

try:
    from .setup import router as setup_router
except Exception:
    setup_router = None

try:
    from .schedule.runner import router as schedule_router
except Exception:
    schedule_router = None


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    # IMPORTANT: include gate first so its handlers aren’t shadowed
    dp.include_router(gate_router)

    if setup_router:
        dp.include_router(setup_router)
    if schedule_router:
        dp.include_router(schedule_router)

    # /start -> hand off to menu.start if available
    if menu_start:
        @dp.message(CommandStart())
        async def _start(m: Message):
            await menu_start(m)

    return dp


async def main():
    logging.basicConfig(level=logging.INFO)
    token = MAIN_BOT_TOKEN or os.getenv("MAIN_BOT_TOKEN")
    if not token:
        raise RuntimeError("MAIN_BOT_TOKEN is not set")
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = build_dispatcher()
    logging.info("Spinify Main Bot starting polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
