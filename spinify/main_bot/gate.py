from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums.chat_member_status import ChatMemberStatus

from ..common.config import OWNER_ID, GATE_PUBLIC_USERNAME, GATE_PRIVATE_INVITE
from ..common.db import set_setting, get_setting, set_agreed

router = Router()


async def send_gate(m: Message) -> None:
    """
    Sends the gate message requiring users to join required channels and agree to the T&C.
    Called by /start before opening the main menu.
    """
    text = (
        "\U0001F6AA <b>Access Required</b>\n"
        "Please join the required channels and then tap <b>I Agree</b> to continue."
    )
    kb = _kb(m.from_user.id)
    await m.answer(text, reply_markup=kb)

def _kb():
    pub = (GATE_PUBLIC_USERNAME or "").lstrip("@")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Join-1 — @{pub}" if pub else "Join-1",
                              url=f"https://t.me/{pub}" if pub else "https://t.me")],
        [InlineKeyboardButton(text="Join-2 — Private GC",
                              url=GATE_PRIVATE_INVITE or "https://t.me")],
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
    except Exception:
        return False

async def gate_ok(bot, uid: int):
    pub_ok = True
    if GATE_PUBLIC_USERNAME:
        pub_ok = await _is_member(bot, f"@{GATE_PUBLIC_USERNAME.lstrip('@')}", uid)
    pid = get_setting("gate.private_id")
    priv_ok = True
    if pid:
        try:
            priv_ok = await _is_member(bot, int(pid), uid)
        except Exception:
            priv_ok = True
    return pub_ok and priv_ok

@router.message(Command("capture_here"))
async def capture_here(m: Message):
    if m.from_user.id != OWNER_ID:
        await m.reply("Only the owner can use /capture_here. Check OWNER_ID in .env.")
        return
    set_setting("gate.private_id", str(m.chat.id))
    await m.reply(f"Captured private chat_id: {m.chat.id}")

@router.message(Command("set_gate"))
async def set_gate(m: Message):
    if m.from_user.id != OWNER_ID:
        await m.reply("Only the owner can use /set_gate.")
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

@router.callback_query(F.data == "gate_check")
async def cb_check(c: CallbackQuery):
    ok = await gate_ok(c.bot, c.from_user.id)
    await c.answer("✅ Both joined" if ok else "❗Still missing one join", show_alert=True)

@router.callback_query(F.data == "gate_agree")
async def cb_agree(c: CallbackQuery):
    if not await gate_ok(c.bot, c.from_user.id):
        await c.answer("Join both first.", show_alert=True)
        return
    set_agreed(c.from_user.id, True)
    try:
        await c.message.edit_text("✅ You’re set.")
    except Exception:
        pass
    # Auto-open main menu after Agree (uses your existing menu.py start handler)
    try:
        from .menu import start as menu_start
        await menu_start(c.message)
    except Exception:
        await c.message.answer("You’re set. Now send /start to open the menu.")
    # Always answer the callback last to clear Telegram's loading spinner
    await c.answer()
