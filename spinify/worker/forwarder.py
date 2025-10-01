from telethon import TelegramClient
from telethon.sessions import StringSession
from ..common.db import (
    get_active_session_enc, bump_counters,
    pick_weighted_ad, mark_group_sent, _conn
)
from ..common.security import decrypt_text
from ..common.config import MAIN_BOT_USERNAME, COOLDOWN_MIN, MAX_PER_TICK

async def _groups_ready_links(tg_id:int):
    c = _conn()
    rows = c.execute(f"""
        SELECT link, title, last_sent_at
        FROM groups
        WHERE tg_id=? AND active=1
          AND (last_sent_at IS NULL OR datetime(last_sent_at,'+{COOLDOWN_MIN} minutes') <= datetime('now','localtime'))
        ORDER BY last_sent_at IS NOT NULL, id ASC
    """, (tg_id,)).fetchall()
    c.close(); return rows

async def process_tick(tg_id: int):
    enc = get_active_session_enc(tg_id)
    if not enc: return
    string_session = decrypt_text(enc)
    client = TelegramClient(StringSession(string_session), api_id=0, api_hash="")
    await client.connect()
    try:
        groups = await _groups_ready_links(tg_id)
        if not groups: return
        sent_count = 0
        for g in groups:
            if sent_count >= MAX_PER_TICK:
                break
            ad = pick_weighted_ad(tg_id)
            if not ad: return
            ad_id, ad_link = ad["id"], ad["msg_link"]

            ok = False
            try:
                res = await client.inline_query(MAIN_BOT_USERNAME, f"send:{ad_id}")
                if res:
                    await res[0].click(g["link"])   # target via saved t.me/@ link
                    ok = True
            except Exception:
                ok = False

            if not ok:
                try:
                    await client.send_message(g["link"], ad_link)
                    ok = True
                except Exception:
                    ok = False

            if ok:
                sent_count += 1
                # record last_sent
                try:
                    ent = await client.get_entity(g["link"])
                    from telethon.utils import get_peer_id
                    peer_id = get_peer_id(ent)
                except Exception:
                    peer_id = 0
                mark_group_sent(tg_id, peer_id or 0)
                bump_counters(tg_id, is_ad=True)
    finally:
        await client.disconnect()
