from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums.chat_member_status import ChatMemberStatus
from ..common.config import OWNER_ID, GATE_PUBLIC_USERNAME, GATE_PRIVATE_INVITE
from ..common.db import set_setting, get_setting, set_agreed, agreed

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
        return m.status in {ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED}
    except: return False

async def gate_ok(bot, uid:int):
    pub = await _is_member(bot, GATE_PUBLIC_USERNAME, uid)
    pid = get_setting("gate.private_id")
    priv = await _is_member(bot, int(pid), uid) if pid else False
    return pub and priv

async def send_gate(m: Message):
    await m.answer(
        "Before using Spinify, please join both channels below, tap “✅ I’ve Joined”, then agree to the Terms.",
        reply_markup=_kb(),
        disable_web_page_preview=True
    )

@router.message(Command("capture_here"))
async def capture_here(m: Message):
    if m.from_user.id != OWNER_ID: return
    set_setting("gate.private_id", str(m.chat.id))
    await m.reply(f"Captured private chat_id: {m.chat.id}")

@router.callback_query(F.data == "gate_check")
async def cb_check(c: CallbackQuery):
    ok = await gate_ok(c.bot, c.from_user.id)
    await c.answer("✅ Both joined" if ok else "❗Still missing one join", show_alert=True)

@router.callback_query(F.data == "gate_agree")
async def cb_agree(c: CallbackQuery):
    if not await gate_ok(c.bot, c.from_user.id):
        await c.answer("Join both first.", show_alert=True); return
    set_agreed(c.from_user.id, True)
    await c.message.edit_text("✅ You're set. Send /start again.")
    await c.answer()
  
