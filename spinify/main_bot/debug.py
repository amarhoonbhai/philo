# spinify/main_bot/debug.py
from aiogram import Router
from aiogram.types import CallbackQuery

router = Router(name="debug_callbacks")

@router.callback_query()
async def _debug_all_callbacks(c: CallbackQuery):
    # Always answer to stop the loading spinner
    try:
        await c.answer()
    except Exception:
        pass
    # Print to stdout; check with: tail -f ~/philo/main.log
    print("[CB]", c.from_user.id, c.data)
  
