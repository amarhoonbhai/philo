from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from .keyboards import main_menu, inline_login
from .gate import send_gate, gate_ok
from ..common.db import init_core, ensure_user, agreed
from ..common.config import QUICK_GUIDE_URL, LOGIN_BOT_TOKEN  # username is better if you have it

router = Router()
LOGIN_BOT_USERNAME = "SpinifyLoginBot"

@router.message(CommandStart())
async def start(m: Message):
    init_core(); ensure_user(m.from_user.id)
    if not await gate_ok(m.bot, m.from_user.id) or not agreed(m.from_user.id):
        await send_gate(m); return
    await m.answer("Main menu:", reply_markup=main_menu(), parse_mode=ParseMode.HTML)

@router.message(lambda msg: msg.text == "📣 Ads Manager")
async def ads_manager(m: Message):
    # if no session yet, show open-login button
    url = f"https://t.me/{LOGIN_BOT_USERNAME}?start={m.from_user.id}"
    await m.answer("No accounts linked yet. Use the Login bot first.", reply_markup=inline_login(url, QUICK_GUIDE_URL))
  
