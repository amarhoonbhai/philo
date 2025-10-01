from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest

from ..common.db import get_active_session_enc, set_branding_choice
from ..common.security import decrypt_text

router = Router()

BRAND_NAME_SUFFIX = " — via @SpinifyAdsBot"
BRAND_BIO = "#1 Free Ads Bot — Join @PhiloBots"

async def prompt_branding(bot, user_id: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Apply branding", callback_data="brand_apply")],
        [InlineKeyboardButton(text="Skip", callback_data="brand_skip")],
    ])
    await bot.send_message(
        user_id,
        "Would you like me to set small profile branding?\n"
        f"• Name suffix: <code>{BRAND_NAME_SUFFIX}</code>\n"
        f"• Bio: <code>{BRAND_BIO}</code>",
        reply_markup=kb
    )

@router.message(Command("branding"))
async def cmd_branding(m: Message):
    await prompt_branding(m.bot, m.from_user.id)

@router.message(CommandStart())
async def deeplink_brand(m: Message):
    # supports /start brand
    parts = (m.text or "").split(maxsplit=1)
    if len(parts) == 2 and parts[1].strip().lower() == "brand":
        await prompt_branding(m.bot, m.from_user.id)

@router.callback_query(F.data == "brand_apply")
async def brand_apply(c: CallbackQuery):
    enc = get_active_session_enc(c.from_user.id)
    if not enc:
        await c.answer("No session found. Log in first.", show_alert=True); return
    ss = decrypt_text(enc)
    client = TelegramClient(StringSession(ss), api_id=0, api_hash="")
    await client.connect()
    try:
        me = await client.get_me()
        first = (me.first_name or "")
        if not first.endswith(BRAND_NAME_SUFFIX):
            first = (first + BRAND_NAME_SUFFIX)[:64]  # Telegram limit
        await client(UpdateProfileRequest(first_name=first, about=BRAND_BIO[:70]))
        set_branding_choice(c.from_user.id, True)
        await c.message.edit_text("✅ Branding applied. You can change it anytime in Telegram settings.")
    except Exception:
        await c.answer("Could not update profile.", show_alert=True)
    finally:
        await client.disconnect()

@router.callback_query(F.data == "brand_skip")
async def brand_skip(c: CallbackQuery):
    set_branding_choice(c.from_user.id, False)
    await c.message.edit_text("No problem — you can enable branding later with /branding.")
  
