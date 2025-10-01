import pytz, time
from datetime import datetime, time as dtime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ...common.db import _conn
from ...worker.forwarder import process_tick
from ...worker.guard import ensure_membership_or_pause

scheduler = AsyncIOScheduler()
TZ = pytz.timezone("Asia/Kolkata")

def _within_window(now_local: datetime, start_str: str, end_str: str) -> bool:
    s = dtime.fromisoformat(start_str); e = dtime.fromisoformat(end_str)
    return s <= now_local.time() <= e

def _cycle_active(tg_id:int) -> bool:
    """3h ON / 1h OFF repeating, aligned globally (simple modulo)."""
    now = int(time.time())
    elapsed = now % (4*3600)   # 4h cycle
    return elapsed < (3*3600)  # first 3h = ON

async def _tick(user_tg_id: int):
    now_local = datetime.now(TZ)
    c = _conn()
    sch = c.execute("SELECT window_start, window_end, running FROM schedules WHERE tg_id=?", (user_tg_id,)).fetchone()
    c.close()
    if not sch or not sch["running"]:
        return
    if not _cycle_active(user_tg_id):
        return
    if not _within_window(now_local, sch["window_start"], sch["window_end"]):
        return

    ok, _ = await ensure_membership_or_pause(user_tg_id)
    if not ok:
        return
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
