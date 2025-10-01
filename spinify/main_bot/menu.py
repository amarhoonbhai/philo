# spinify/main_bot/menu.py
# Aiogram v3 router for /start, main menu, Ads Manager, and basic start/stop controls.
# - Enforces join-gate: users must pass gate before seeing menu (uses gate.py).
# - Shows a compact status card (session, window, interval, engine, counters).
# - Provides Ads Manager with quick actions (Setup / Start / Stop / How-to).
# - Uses env var LOGIN_BOT_USERNAME (fallback: "SpinifyLoginBot") for deep-link.

import os
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from .keyboards import main_menu, inline_login
from .gate import send_gate, gate_ok
from ..common.db import (
    init_core, init_bot_tables, ensure_user,
    agreed, has_session, set_running, _conn
)
from ..common.config import QUICK_GUIDE_URL, PREMIUM_URL
from .schedule.runner import refresh_jobs

router = Router()
LOGIN_BOT_USERNAME = os.getenv("LOGIN_BOT_USERNAME", "SpinifyLoginBot")


# ----------------------------
# Helpers
# ----------------------------

def _ads_manager_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Setup Campaigns", callback_data="ads_setup")],
        [
            InlineKeyboardButton(text="🚀 Start", callback_data="ads_start"),
            InlineKeyboardButton(text="⏸️ Stop",  callback_data="ads_stop"),
        ],
        [InlineKeyboardButton(text="❓ How to", url=QUICK_GUIDE_URL)],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")],
    ])


def _premium_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Buy Premium", url=PREMIUM_URL),
            InlineKeyboardButton(text="OK, got it", callback_data="ok_got_it"),
        ]
    ])


def _status_text(tg_id: int) -> str:
    # Pull a compact snapshot from DB (schedule + counters + session flag)
    c = _conn()
    sch = c.execute(
        "SELECT interval_sec, window_start, window_end, running FROM schedules WHERE tg_id=?",
        (tg_id,),
    ).fetchone()
    ctr = c.execute(
        "SELECT total_sent, ads_sent, last_sent FROM counters WHERE tg_id=?",
        (tg_id,),
    ).fetchone()
    c.close()

    has = has_session(tg_id)
    linked = "🟢 Linked" if has else "🔴 Not linked"
    engine = "▶️ Running" if (sch and sch["running"]) else "⏸️ Stopped"
    when = f'{sch["window_start"]}–{sch["window_end"]}' if sch else "06:00–12:00"
    every = f'every {int((sch["interval_sec"] or 1200)/60)} min' if sch else "every 20 min"
    totals = f'{(ctr["total_sent"] if ctr else 0)} total / {(ctr["ads_sent"] if ctr else 0)} ads'
    last = (ctr["last_sent"] if ctr and ctr["last_sent"] else "—")

    return (
        "<b>Spinify — Status</b>\n"
        f"• Account: {linked}\n"
        f"• Window: {when}   • Interval: {every}\n"
        f"• Engine: {engine}\n"
        f"• Sent: {totals}\n"
        f"• Last send: {last}"
    )


# ----------------------------
# Handlers
# ----------------------------

@router.message(CommandStart())
async def start(m: Message):
    # Ensure base tables exist
    init_core()
    init_bot_tables()
    ensure_user(m.from_user.id)

    # Join-gate enforcement
    if not await gate_ok(m.bot, m.from_user.id) or not agreed(m.from_user.id):
        await send_gate(m)
        return

    # Main menu + live status card
    await m.answer("Main menu:", reply_markup=main_menu(), parse_mode=ParseMode.HTML)
    await m.answer(_status_text(m.from_user.id), parse_mode=ParseMode.HTML)


@router.message(F.text == "📣 Ads Manager")
async def ads_manager(m: Message):
    # Gate check (in case user skipped /start)
    if not await gate_ok(m.bot, m.from_user.id) or not agreed(m.from_user.id):
        await send_gate(m)
        return

    # If no session, deep link to Login Bot
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
