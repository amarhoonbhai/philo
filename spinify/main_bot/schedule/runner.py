import pytz
from datetime import datetime, time as dtime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ...common.db import _conn, get_schedule
from ...worker.forwarder import process_tick

scheduler = AsyncIOScheduler()
TZ = pytz.timezone("Asia/Kolkata")

def _within_window(now_local: datetime, start_str: str, end_str: str) -> bool:
    s = dtime.fromisoformat(start_str); e = dtime.fromisoformat(end_str)
    return s <= now_local.time() <= e

async def _tick(user_tg_id: int):
    sch = get_schedule(user_tg_id)
    now = datetime.now(TZ)
    if _within_window(now, sch["window_start"], sch["window_end"]):
        await process_tick(user_tg_id)

def refresh_jobs():
    if not scheduler.running:
        scheduler.start()
    for job in list(scheduler.get_jobs()):
        scheduler.remove_job(job.id)
    c = _conn()
    rows = c.execute("SELECT tg_id, interval_sec FROM schedules WHERE running=1").fetchall()
    c.close()
    for r in rows:
        scheduler.add_job(_tick, "interval", seconds=r["interval_sec"], args=[r["tg_id"]], id=f"user_{r['tg_id']}")
      
