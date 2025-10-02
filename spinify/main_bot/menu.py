# spinify/main_bot/menu.py
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from .keyboards import main_menu, inline_login
from .gate import send_gate, gate_ok
from ..common.db import init_core, ensure_user, agreed  # add has_session if you want to branch
from ..common.config import QUICK_GUIDE_URL
import os

router = Router()

# Read from env so you can change it in /opt/spinify/.env without code edits
LOGIN_BOT_USERNAME = os.getenv("LOGIN_BOT_USERNAME", "SpinifyLoginBot")

@router.message(CommandStart())
async def start(m: Message):
    # Safe to call multiple times
    init_core()
    ensure_user(m.from_user.id)

    # Enforce gate + agreement
    if (not await gate_ok(m.bot, m.from_user.id)) or (not agreed(m.from_user.id)):
        await send_gate(m)
        return

    # Show main menu
    await m.answer("Main menu:", reply_markup=main_menu())

@router.message(F.text == "📣 Ads Manager")
async def ads_manager(m: Message):
    # If you want to branch on saved sessions, import has_session and check here.
    login_deeplink = f"https://t.me/{LOGIN_BOT_USERNAME}?start={m.from_user.id}"
    await m.answer(
        "No accounts linked yet. Use the Login bot first.",
        reply_markup=inline_login(login_deeplink, QUICK_GUIDE_URL)
    )
    if not has_session(m.from_user.id):
        url = f"https://t.me/{LOGIN_BOT_USERNAME}?start={m.from_user.id}"
        await m.answer(
            "No accounts linked yet. Use the Login bot first.",
            reply_markup=inline_login(url, QUICK_GUIDE_URL),
        )
        return

    # Otherwise show status + quick actions
    await m.answer(_status_text(m.from_user.id), parse_mode=ParseMode.HTML, reply_markup=_ads_manager_kb())


@router.message(F.text == "✏️ Customize Name")
async def customize_name(m: Message):
    txt = (
        "<b>Go Premium — $5/mo 🚀</b>\n"
        "Unlock multiple accounts, post rotation, and priority sending."
    )
    await m.answer(txt, parse_mode=ParseMode.HTML, reply_markup=_premium_kb())


@router.message(F.text == "📨 Total Messages Sent")
async def total_messages(m: Message):
    c = _conn()
    r = c.execute("SELECT total_sent FROM counters WHERE tg_id=?", (m.from_user.id,)).fetchone()
    c.close()
    total = r["total_sent"] if r else 0
    await m.answer(f"📨 Total Messages Sent: <b>{total}</b>", parse_mode=ParseMode.HTML)


@router.message(F.text == "📊 Ads Message Total Sent")
async def ads_messages(m: Message):
    c = _conn()
    r = c.execute("SELECT ads_sent FROM counters WHERE tg_id=?", (m.from_user.id,)).fetchone()
    c.close()
    total = r["ads_sent"] if r else 0
    await m.answer(f"📊 Ads Message Total Sent: <b>{total}</b>", parse_mode=ParseMode.HTML)


# ----- Inline callbacks for Ads Manager -----

@router.callback_query(F.data == "ads_setup")
async def cb_setup(c: CallbackQuery):
    # Place your setup UI here or route to your existing /set_ad, /add_group, /set_interval flows
    await c.answer("Setup opened.", show_alert=False)


@router.callback_query(F.data == "ads_start")
async def cb_start(c: CallbackQuery):
    set_running(c.from_user.id, True)
    refresh_jobs()
    await c.answer("Started ✅", show_alert=True)
    # Refresh status card
    await c.message.edit_text(_status_text(c.from_user.id), parse_mode=ParseMode.HTML, reply_markup=_ads_manager_kb())


@router.callback_query(F.data == "ads_stop")
async def cb_stop(c: CallbackQuery):
    set_running(c.from_user.id, False)
    refresh_jobs()
    await c.answer("Stopped ⏸️", show_alert=True)
    # Refresh status card
    await c.message.edit_text(_status_text(c.from_user.id), parse_mode=ParseMode.HTML, reply_markup=_ads_manager_kb())


@router.callback_query(F.data == "back_main")
async def cb_back(c: CallbackQuery):
    await c.message.edit_text("Main menu:", parse_mode=ParseMode.HTML)
    await c.message.answer(_status_text(c.from_user.id), parse_mode=ParseMode.HTML)
    await c.answer()


@router.callback_query(F.data == "ok_got_it")
async def cb_ok(c: CallbackQuery):
    await c.answer()
