import pytz
from datetime import datetime, time as dtime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ...common.db import _conn

scheduler = AsyncIOScheduler()
TZ = pytz.timezone("Asia/Kolkata")

def _within(now_local: datetime, start_str: str, end_str: str) -> bool:
    s = dtime.fromisoformat(start_str); e = dtime.fromisoformat(end_str)
    return s <= now_local.time() <= e

async def _tick(tg_id: int):
    c = _conn()
    sch = c.execute("SELECT window_start,window_end FROM schedules WHERE tg_id=?", (tg_id,)).fetchone()
    c.close()
    now = datetime.now(TZ)
    if sch and _within(now, sch["window_start"], sch["window_end"]):
        # TODO: enqueue worker task; for now it's a stub
        pass

def refresh_jobs():
    if not scheduler.running:
        scheduler.start()
    for j in list(scheduler.get_jobs()):
        scheduler.remove_job(j.id)
    c = _conn()
    rows = c.execute("SELECT tg_id, interval_sec FROM schedules WHERE running=1").fetchall()
    c.close()
    for r in rows:
        scheduler.add_job(_tick, "interval", seconds=r["interval_sec"], args=[r["tg_id"]], id=f"user_{r['tg_id']}")
