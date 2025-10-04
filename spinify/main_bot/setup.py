from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from .keyboards import setup_root_kb, groups_menu_kb, ads_menu_kb, sched_menu_kb, main_menu
from ..common.db import (
    add_group_link, list_groups_links, del_group_link, groups_count,
    add_ad, list_ads, del_ad, _conn,
    set_interval_minutes, set_window,
    get_active_session_enc
)
from ..common.security import decrypt_text
from telethon import TelegramClient
from telethon.sessions import StringSession

router = Router()

class S(StatesGroup):
    GROUP_ADD_LINK = State()
    GROUP_DEL_LINK = State()
    AD_ADD = State()
    AD_DEL = State()
    AD_W = State()
    S_WIN = State()

async def _resolve_title_with_session(tg_id:int, link:str) -> str:
    """Try to resolve a nice title using the user's Telethon session (optional)."""
    enc = get_active_session_enc(tg_id)
    if not enc:
        return link
    ss = decrypt_text(enc)
    client = TelegramClient(StringSession(ss), api_id=0, api_hash="")
    await client.connect()
    try:
        ent = await client.get_entity(link)
        title = getattr(ent, "title", None) or getattr(ent, "username", None) or link
        return title
    except Exception:
        return link
    finally:
        await client.disconnect()

# ---- Entry ----
@router.callback_query(F.data == "ads_setup")
@router.message(Command("setup"))
async def setup_home(e):
    msg = e.message if isinstance(e, CallbackQuery) else e
    await msg.answer("⚙️ All ads setup is here:", reply_markup=setup_root_kb())

@router.callback_query(F.data == "setup_home")
async def cb_setup_home(c: CallbackQuery):
    await c.message.edit_text("⚙️ All ads setup is here:", reply_markup=setup_root_kb()); await c.answer()

# ---- Groups by link ----
@router.callback_query(F.data == "setup_groups")
async def cb_groups(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.edit_text("👥 Groups — manage up to <b>5</b> GCs by link.", reply_markup=groups_menu_kb(), parse_mode="HTML"); await c.answer()

@router.callback_query(F.data == "groups_add_link")
async def groups_add_link(c: CallbackQuery, state: FSMContext):
    if groups_count(c.from_user.id) >= 5:
        await c.answer("Limit reached: max 5 groups.", show_alert=True); return
    await c.message.edit_text(
        "Send the group link (e.g. <code>https://t.me/YourGroup</code> or <code>@YourGroup</code>).",
        parse_mode="HTML", reply_markup=groups_menu_kb()
    )
    await state.set_state(S.GROUP_ADD_LINK); await c.answer()

@router.message(S.GROUP_ADD_LINK)
async def groups_add_link_do(m: Message, state: FSMContext):
    link = (m.text or "").strip()
    if not (link.startswith("http") or link.startswith("@")):
        await m.answer("Please send a valid t.me link or @username."); return
    title = await _resolve_title_with_session(m.from_user.id, link)
    try:
        add_group_link(m.from_user.id, link, title)
        await m.answer(f"✅ Added GC: <b>{title}</b>\n<code>{link}</code>", parse_mode="HTML")
    except ValueError:
        await m.answer("Limit reached: you already have 5 groups.")
    await state.clear()

@router.callback_query(F.data == "groups_list")
async def groups_list_cb(c: CallbackQuery):
    rows = list_groups_links(c.from_user.id)
    if not rows:
        await c.answer("No groups yet.", show_alert=True); return
    text = "👥 Groups (max 5):\n" + "\n".join([f"• {r['title']} — <code>{r['link']}</code>" for r in rows])
    await c.message.edit_text(text, parse_mode="HTML", reply_markup=groups_menu_kb())

@router.callback_query(F.data == "groups_del_link")
async def groups_del_link(c: CallbackQuery, state: FSMContext):
    await c.message.edit_text("Send the group link exactly as saved to delete it.", reply_markup=groups_menu_kb())
    await state.set_state(S.GROUP_DEL_LINK); await c.answer()

@router.message(S.GROUP_DEL_LINK)
async def groups_del_link_do(m: Message, state: FSMContext):
    link = (m.text or "").strip()
    del_group_link(m.from_user.id, link)
    await m.answer(f"🗑 Deleted GC: <code>{link}</code>", parse_mode="HTML")
    await state.clear()

# ---- Ads ----
@router.callback_query(F.data == "setup_ads")
async def cb_ads(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.edit_text("🧷 Ads — choose an action:", reply_markup=ads_menu_kb()); await c.answer()

@router.callback_query(F.data == "ads_add")
async def ads_add_cb(c: CallbackQuery, state: FSMContext):
    await c.message.edit_text("Paste a Telegram message link (e.g. https://t.me/c/XXXX/YYY or https://t.me/channel/123).")
    await state.set_state(S.AD_ADD); await c.answer()

@router.message(S.AD_ADD)
async def ads_add_do(m: Message, state: FSMContext):
    link = (m.text or "").strip()
    if not link.startswith("http"):
        await m.answer("Send a valid message link."); return
    add_ad(m.from_user.id, link, 1)
    await m.answer("✅ Ad saved.")
    await state.clear()

@router.callback_query(F.data == "ads_list")
async def ads_list_cb(c: CallbackQuery):
    rows = list_ads(c.from_user.id)
    if not rows:
        await c.answer("No ads yet.", show_alert=True); return
    text = "🧷 Ads:\n" + "\n".join([f"• id={r['id']} — <code>{r['msg_link']}</code> (w={r['weight']})" for r in rows])
    await c.message.edit_text(text, parse_mode="HTML", reply_markup=ads_menu_kb())

@router.callback_query(F.data == "ads_del")
async def ads_del_cb(c: CallbackQuery, state: FSMContext):
    await c.message.edit_text("Send the <code>ad_id</code> to delete.", parse_mode="HTML", reply_markup=ads_menu_kb())
    await state.set_state(S.AD_DEL); await c.answer()

@router.message(S.AD_DEL)
async def ads_del_do(m: Message, state: FSMContext):
    try:
        ad_id = int((m.text or "").strip())
        del_ad(m.from_user.id, ad_id)
        await m.answer(f"🗑 Deleted ad id={ad_id}.")
    except Exception:
        await m.answer("Invalid ad_id.")
    await state.clear()

@router.callback_query(F.data == "ads_weight")
async def ads_weight_cb(c: CallbackQuery, state: FSMContext):
    await c.message.edit_text("Send: <code>ad_id weight</code>  (e.g. <b>12 5</b>)", parse_mode="HTML", reply_markup=ads_menu_kb())
    await state.set_state(S.AD_W); await c.answer()

@router.message(S.AD_W)
async def ads_weight_do(m: Message, state: FSMContext):
    try:
        ad_id_s, w_s = (m.text or "").strip().split()
        ad_id = int(ad_id_s); w = max(1, int(w_s))
        c=_conn(); c.execute("UPDATE ads SET weight=? WHERE tg_id=? AND id=?", (w, m.from_user.id, ad_id)); c.commit(); c.close()
        await m.answer(f"✅ Weight set: ad_id={ad_id} → {w}")
    except Exception:
        await m.answer("Format must be: <code>ad_id weight</code>")
    await state.clear()

# ---- Schedule ----
@router.callback_query(F.data == "setup_sched")
async def cb_sched(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.edit_text(
        "⏱ Scheduler — choose an interval preset (20m/40m/60m).\n"
        "Cycle runs <b>3h ON</b> → <b>1h OFF</b> automatically.",
        parse_mode="HTML", reply_markup=sched_menu_kb()
    ); await c.answer()

@router.callback_query(F.data.in_(["sched_20","sched_40","sched_60"]))
async def sched_presets(c: CallbackQuery):
    mins = {"sched_20":20, "sched_40":40, "sched_60":60}[c.data]
    set_interval_minutes(c.from_user.id, mins)
    await c.answer(f"Interval set: every {mins} min", show_alert=True)

@router.callback_query(F.data == "sched_win")
async def sched_win_cb(c: CallbackQuery, state: FSMContext):
    await c.message.edit_text("Send window as HH:MM-HH:MM (e.g. 06:00-12:00).", reply_markup=sched_menu_kb())
    await state.set_state(S.S_WIN); await c.answer()

@router.message(S.S_WIN)
async def sched_win_do(m: Message, state: FSMContext):
    try:
        a,b = (m.text or "").strip().split("-",1)
        set_window(m.from_user.id, a.strip(), b.strip())
        await m.answer("✅ Window updated.")
    except Exception:
        await m.answer("Format must be HH:MM-HH:MM (e.g. 06:00-12:00).")
    await state.clear()

@router.callback_query(F.data == "sched_info")
async def sched_info(c: CallbackQuery):
    await c.answer("The engine runs 3 hours, pauses 1 hour, then repeats.", show_alert=True)

# ---- Back from setup root ----
@router.callback_query(F.data == "back_ads_home")
async def cb_back_ads_home(c: CallbackQuery):
    """
    Handle the "Back" button from the setup screens. When users tap the
    back arrow in the setup menu, return them to the main menu. This
    implementation mirrors the behaviour of the back button in the Ads
    Manager. It edits the current message and then sends the main menu
    keyboard to the chat.
    """
    try:
        # Edit the existing setup message to a minimal text to avoid clutter
        await c.message.edit_text("Main menu:", parse_mode="HTML")
    except Exception:
        # If edit fails (e.g. message deleted), ignore
        pass
    # Send main menu keyboard in a new message
    await c.message.answer("Main menu:", parse_mode="HTML", reply_markup=main_menu())
    await c.answer()
  
