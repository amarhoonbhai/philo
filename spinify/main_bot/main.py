# spinify/main_bot/main.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

from ..common.config import MAIN_BOT_TOKEN
from ..common.db import init_core, init_bot_tables
from .schedule.runner import refresh_jobs

# Routers (required)
from .menu import router as menu_router

# Optional routers (include if present)
try:
    from .inline import router as inline_router
except Exception:  # pragma: no cover
    inline_router = None

try:
    from .setup import router as setup_router
except Exception:  # pragma: no cover
    setup_router = None

# Optional: debug router that logs/answers all callbacks (if you created spinify/main_bot/debug.py)
try:
    from .debug import router as debug_router
except Exception:  # pragma: no cover
    debug_router = None

# Dispatcher shared across run scripts if needed
dp = Dispatcher()


def _make_bot() -> Bot:
    """
    aiogram 3.7-compatible Bot factory.
    NOTE: AiohttpSession(timeout=...) expects seconds (int/float), not ClientTimeout.
    """
    session = AiohttpSession(timeout=30)
    return Bot(
        MAIN_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )


async def boot() -> None:
    """Initialize DB and wire routers & scheduler. Safe to call once at startup."""
    # DB bootstrap (idempotent)
    init_core()
    init_bot_tables()

    # Include routers
    dp.include_router(menu_router)
    if inline_router:
        dp.include_router(inline_router)
    if setup_router:
        dp.include_router(setup_router)
    if debug_router:
        dp.include_router(debug_router)

    # Start scheduler jobs (3h ON / 1h OFF, plus any window checks)
    refresh_jobs()


async def main() -> None:
    bot = _make_bot()
    await boot()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
