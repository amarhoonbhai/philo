from aiogram import Bot
from aiogram.enums.chat_member_status import ChatMemberStatus
from ..common.config import MAIN_BOT_TOKEN, GATE_PUBLIC_USERNAME
from ..common.db import get_setting, set_running

_bot = Bot(MAIN_BOT_TOKEN)

async def _is_member(chat, user_id: int) -> bool:
    try:
        m = await _bot.get_chat_member(chat_id=chat, user_id=user_id)
        return m.status in {
            ChatMemberStatus.CREATOR,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.RESTRICTED,
        }
    except Exception:
        return False

async def ensure_membership_or_pause(user_id: int):
    """
    Soft enforcement:
      - If user not in @PhiloBots or the private GC, pause their engine and DM a notice.
      - Return (ok, missing_list)
    """
    pub_ok = await _is_member(GATE_PUBLIC_USERNAME, user_id)
    pid = get_setting("gate.private_id")
    priv_ok = await _is_member(int(pid), user_id) if pid else False

    if pub_ok and priv_ok:
        return True, []

    # Pause engine and notify
    set_running(user_id, False)
    missing = []
    if not pub_ok:
        missing.append("@PhiloBots")
    if not priv_ok:
        missing.append("private GC")

    try:
        await _bot.send_message(
            user_id,
            "⏸️ Your ad engine is paused.\n"
            "You must stay in: " + ", ".join(missing) + ".\n"
            "Rejoin and press /start or use 'Recheck & Resume' in Account."
        )
    except Exception:
        pass

    return False, missing
  
