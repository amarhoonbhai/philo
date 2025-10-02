# spinify/main_bot/gate.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums.chat_member_status import ChatMemberStatus

from ..common.config import OWNER_ID, GATE_PUBLIC_USERNAME, GATE_PRIVATE_INVITE
from ..common.db import set_setting, get_setting, set_agreed

router = Router()

def _kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Join-1 — @PhiloBots", url="https://t.me/PhiloBots")],
        [InlineKeyboardButton(text="Join-2 — Private GC", url=GATE_PRIVATE_INVITE)],
        [InlineKeyboardButton(text="✅ I’ve Joined", callback_data="gate_check")],
        [InlineKeyboardButton(text="📜 Agree Terms & Conditions", callback_data="gate_agree")],
    ])

async def _is_member(bot, chat, uid):
    try:
        m = await bot.get_chat_member(chat, uid)
        return m.status in {
            ChatMemberStatus.CREATOR,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.RESTRICTED
        }
    except:
        return False

async def gate_ok(bot, uid:int):
    pub = await _is_member(bot, GATE_PUBLIC_USERNAME, uid) if GATE_PUBLIC_USERNAME else True
    pid = get_setting("gate.private_id")
    priv = await _is_member(bot, int(pid), uid) if pid else False
    return pub and priv

async def send_gate(m: Message):
    await m.answer(
        "Before using Spinify, please join both channels below, tap “✅ I’ve Joined”, then agree to the Terms.",
        reply_markup=_kb(),
        disable_web_page_preview=True
    )

# ---------- Owner utilities ----------

@router.message(Command("capture_here"))
async def capture_here(m: Message):
    if m.from_user.id != OWNER_ID:
        await m.reply("Only the bot owner can use /capture_here. Set OWNER_ID in env and try again.")
        return
    set_setting("gate.private_id", str(m.chat.id))
    await m.reply(f"Captured private chat_id: {m.chat.id}")

@router.message(Command("set_gate"))
async def set_gate(m: Message):
    if m.from_user.id != OWNER_ID:
        await m.reply("Only the bot owner can use /set_gate.")
        return
    parts = (m.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await m.reply("Usage: /set_gate -1001234567890")
        return
    chat_id = parts[1].strip()
    set_setting("gate.private_id", chat_id)
    await m.reply(f"Saved private chat_id: {chat_id}")

@router.message(Command("whoami"))
async def whoami(m: Message):
    await m.reply(f"Your user id: <code>{m.from_user.id}</code>", parse_mode="HTML")

# ---------- Gate callbacks ----------

@router.callback_query(F.data == "gate_check")
async def cb_check(c: CallbackQuery):
    ok = await gate_ok(c.bot, c.from_user.id)
    await c.answer("✅ Both joined" if ok else "❗Still missing one join", show_alert=True)

@router.callback_query(F.data == "gate_agree")
async def cb_agree(c: CallbackQuery):
    # Require both joins before agreeing
    if not await gate_ok(c.bot, c.from_user.id):
        await c.answer("Join both first.", show_alert=True)
        return

    set_agreed(c.from_user.id, True)
    # Clean confirmation
    try:
        await c.message.edit_text("✅ You’re set.")
    except Exception:
        pass

    # Auto-open main menu (no need to type /start)
    try:
        from .menu import start as menu_start  # import here to avoid circular import at module load
        await menu_start(c.message)
    except Exception:
        # Fallback instruction if something goes wrong
        await c.message.answer("You’re set. Now send /start to open the menu.")

    await c.answer()
