from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.enums import ParseMode
from ..common.db import list_ads, get_ad_by_id

router = Router()

@router.inline_query()
async def handle_inline(iq: InlineQuery):
    q = (iq.query or "").strip()

    # Direct mode: send a specific ad id → query looks like:  send:123
    if q.startswith("send:"):
        try:
            ad_id = int(q.split(":", 1)[1])
        except Exception:
            ad_id = None
        if ad_id:
            r = get_ad_by_id(iq.from_user.id, ad_id)
            if r:
                await iq.answer(
                    results=[
                        InlineQueryResultArticle(
                            id=str(r["id"]),
                            title=f"Ad #{r['id']}",
                            description=r["msg_link"],
                            input_message_content=InputTextMessageContent(
                                message_text=r["msg_link"],
                                parse_mode=ParseMode.HTML,
                                disable_web_page_preview=False,
                            ),
                        )
                    ],
                    cache_time=1,
                    is_personal=True,
                )
                return

    # Default: show recent ads to pick manually
    rows = list_ads(iq.from_user.id)
    if not rows:
        await iq.answer(
            results=[],
            cache_time=1,
            is_personal=True,
            switch_pm_text="No ads saved — open bot to add",
            switch_pm_parameter="start",
        )
        return

    results = []
    for r in rows[:10]:
        results.append(
            InlineQueryResultArticle(
                id=str(r["id"]),
                title=f"Ad #{r['id']}",
                description=r["msg_link"],
                input_message_content=InputTextMessageContent(
                    message_text=r["msg_link"],
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False,
                ),
            )
        )
    await iq.answer(results, cache_time=1, is_personal=True)
