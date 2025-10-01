# spinify/worker/guard.py
from aiogram import Bot
from aiogram.enums.chat_member_status import ChatMemberStatus

from ..common.config import MAIN_BOT_TOKEN, GATE_PUBLIC_USERNAME, GATE_ENFORCE
from ..common.db import get_setting, set_running

# Reuse a lightweight bot client for membership checks
_bot = Bot(MAIN_BOT_TOKEN)

async def _is_member(chat, user_id: int) -> bool:
    """
    Return True if user is a member/admin/etc.
    If we cannot check (privacy, not admin, invalid id), return True (do not block).
    """
    try:
        m = await _bot.get_chat_member(chat_id=chat, user_id=user_id)
        return m.status in {
            ChatMemberStatus.CREATOR,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.RESTRICTED,
        }
    except Exception:
        # Be tolerant during setup / private channels / non-admin bot, etc.
        return True

async def ensure_membership_or_pause(user_id: int):
    """
    Soft enforcement:
      - If GATE_ENFORCE=0, never block.
      - If public/private checks are not configured or not accessible, don’t block.
      - Otherwise, pause engine and notify the user what is missing.
    """
    if not GATE_ENFORCE:
        return True, []

    pub_ok = True
    if GATE_PUBLIC_USERNAME:
        # Accept @name or name
        chat = GATE_PUBLIC_USERNAME if GATE_PUBLIC_USERNAME.startswith("@") else f"@{GATE_PUBLIC_USERNAME}"
        pub_ok = await _is_member(chat, user_id)

    priv_ok = True
    pid = get_setting("gate.private_id")
    if pid:
        try:
            priv_ok = await _is_member(int(pid), user_id)
        except Exception:
            # Don’t block on private id errors
            priv_ok = True

    if pub_ok and priv_ok:
        return True, []

    # Pause engine and notify user
    set_running(user_id, False)
    missing = []
    if not pub_ok:
        missing.append(GATE_PUBLIC_USERNAME or "@PhiloBots")
    if not priv_ok:
        missing.append("private GC")

    try:
        await _bot.send_message(
            user_id,
            "⏸️ Your ad engine is paused.\n"
            "You must stay in: " + ", ".join(missing) + ".\n"
            "Rejoin and press /start or use the Account menu to resume."
        )
    except Exception:
        pass

    return False, missing
