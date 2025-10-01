from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest
from telethon.tl.types import InputUser
from ..common.db import save_session
from ..common.security import encrypt_text

async def attach_and_prepare(tg_id: int, tl_client, bot_username: str = None):
    """
    Saves the user's StringSession (encrypted) and ensures a 'Spinify — Send Campaign' channel exists.
    Optionally adds your bot as admin to read posts if bot_username provided.
    """
    # 1) Save session
    enc = encrypt_text(tl_client.save_string())
    save_session(tg_id, enc)

    # 2) Create private broadcast channel if missing (best-effort)
    try:
        me = await tl_client.client.get_me()
        title = "Spinify — Send Campaign"
        # Find existing
        dialogs = await tl_client.client.get_dialogs()
        target = None
        for d in dialogs:
            if d.is_channel and d.entity.title == title:
                target = d.entity; break
        if not target:
            res = await tl_client.client(CreateChannelRequest(title, "Post ads here to forward", broadcast=True, megagroup=False))
            target = res.chats[0]
        # 3) Optionally add your bot (read-only)
        if bot_username:
            try:
                bot = await tl_client.client.get_entity(bot_username)
                await tl_client.client(InviteToChannelRequest(target, [InputUser(bot.id, access_hash=bot.access_hash)]))
            except Exception:
                pass
    except Exception:
        pass
      
