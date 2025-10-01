from telethon import TelegramClient
from telethon.sessions import StringSession
from ..common.db import get_active_session_enc, bump_counters, _conn
from ..common.security import decrypt_text

async def _get_groups(tg_id: int):
    c = _conn()
    rows = c.execute("SELECT peer_id, title FROM groups WHERE tg_id=? AND active=1", (tg_id,)).fetchall()
    c.close()
    return [(r["peer_id"], r["title"]) for r in rows]

async def _pick_ad_message_link(tg_id: int) -> str | None:
    c = _conn()
    r = c.execute("""SELECT msg_link FROM ads WHERE tg_id=? AND active=1
                     ORDER BY id DESC LIMIT 1""", (tg_id,)).fetchone()
    c.close()
    return r["msg_link"] if r else None

async def process_tick(tg_id: int):
    enc = get_active_session_enc(tg_id)
    if not enc: return
    string_session = decrypt_text(enc)

    # connect as the user
    client = TelegramClient(StringSession(string_session), api_id=0, api_hash="")  # api_id/hash are embedded in string
    await client.connect()
    try:
        ad_link = await _pick_ad_message_link(tg_id)
        if not ad_link:
            return
        # fetch the message by link (supports channel/chat links)
        msg = await client.get_messages(ad_link, ids=[])
        if not msg:
            try:
                # fallback: parse link text "https://t.me/c/xxxx/yyy"
                pass
            except Exception:
                return

        for peer_id, _title in await _get_groups(tg_id):
            try:
                await client.forward_messages(peer_id, msg)
                bump_counters(tg_id)
            except Exception:
                continue
    finally:
        await client.disconnect()
      
