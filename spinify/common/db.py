import sqlite3, time
from pathlib import Path
from .config import DB_PATH

Path(DB_PATH).touch(exist_ok=True)

def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

# ---------- INIT ----------
def init_core():
    c = _conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
      tg_id INTEGER PRIMARY KEY,
      plan TEXT DEFAULT 'free'
    );
    CREATE TABLE IF NOT EXISTS settings(
      key TEXT PRIMARY KEY,
      value TEXT
    );
    CREATE TABLE IF NOT EXISTS gates(
      tg_id INTEGER PRIMARY KEY,
      agreed_tos INTEGER DEFAULT 0
    );
    -- subscriptions (status & expiry)
    CREATE TABLE IF NOT EXISTS subs(
      tg_id INTEGER PRIMARY KEY,
      plan TEXT DEFAULT 'free',
      until_ts INTEGER DEFAULT 0
    );
    -- optional coupon codes
    CREATE TABLE IF NOT EXISTS coupons(
      code TEXT PRIMARY KEY,
      plan TEXT NOT NULL,
      days INTEGER NOT NULL,
      used_by INTEGER,
      used_at INTEGER
    );
    """)
    c.commit(); c.close()

def init_bot_tables():
    c = _conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS sessions(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      tg_id INTEGER,
      string_session TEXT,
      active INTEGER DEFAULT 1,
      created_at INTEGER
    );
    CREATE TABLE IF NOT EXISTS groups(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      tg_id INTEGER,
      peer_id INTEGER,
      title TEXT,
      active INTEGER DEFAULT 1,
      last_sent_at TEXT
    );
    CREATE TABLE IF NOT EXISTS ads(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      tg_id INTEGER,
      msg_link TEXT,
      weight INTEGER DEFAULT 1,
      active INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS schedules(
      tg_id INTEGER PRIMARY KEY,
      interval_sec INTEGER DEFAULT 1200,
      window_start TEXT DEFAULT '06:00',
      window_end TEXT DEFAULT '12:00',
      running INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS counters(
      tg_id INTEGER PRIMARY KEY,
      total_sent INTEGER DEFAULT 0,
      ads_sent INTEGER DEFAULT 0,
      last_sent TEXT
    );
    """)
    c.execute("INSERT OR IGNORE INTO schedules(tg_id) SELECT tg_id FROM users;")
    c.execute("INSERT OR IGNORE INTO counters(tg_id)  SELECT tg_id FROM users;")
    c.execute("INSERT OR IGNORE INTO subs(tg_id)      SELECT tg_id FROM users;")
    c.commit(); c.close()
    _try_migrate_groups_table()

# --- MIGRATIONS ---
def _try_migrate_groups_table():
    c = _conn()
    try:
        c.execute("ALTER TABLE groups ADD COLUMN link TEXT")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE groups ADD COLUMN created_at TEXT")
    except Exception:
        pass
    c.commit(); c.close()

# ----- settings -----
def set_setting(k,v):
    c=_conn()
    c.execute("""INSERT INTO settings(key,value) VALUES(?,?)
                 ON CONFLICT(key) DO UPDATE SET value=excluded.value""",(k,v))
    c.commit(); c.close()

def get_setting(k):
    c=_conn()
    r=c.execute("SELECT value FROM settings WHERE key=?",(k,)).fetchone()
    c.close(); return r["value"] if r else None

def set_agreed(tg_id,yes):
    c=_conn(); c.execute("UPDATE gates SET agreed_tos=? WHERE tg_id=?",(1 if yes else 0,tg_id))
    c.commit(); c.close()

def agreed(tg_id):
    c=_conn(); r=c.execute("SELECT agreed_tos FROM gates WHERE tg_id=?",(tg_id,)).fetchone()
    c.close(); return bool(r and r["agreed_tos"])

# branding pref
def set_branding_choice(tg_id:int, enabled:bool):
    set_setting(f"branding.{tg_id}", "1" if enabled else "0")

def get_branding_choice(tg_id:int)->bool:
    v = get_setting(f"branding.{tg_id}")
    return v == "1"

# ----- sessions -----
def has_session(tg_id:int)->bool:
    c=_conn(); r=c.execute("SELECT 1 FROM sessions WHERE tg_id=? AND active=1 LIMIT 1",(tg_id,)).fetchone()
    c.close(); return bool(r)

def sessions_count(tg_id:int)->int:
    c=_conn(); r=c.execute("SELECT COUNT(*) AS n FROM sessions WHERE tg_id=? AND active=1",(tg_id,)).fetchone()
    c.close(); return r["n"] if r else 0

def save_session(tg_id:int, enc_string_session:str):
    c=_conn()
    c.execute("""INSERT INTO sessions(tg_id, string_session, active, created_at)
                 VALUES(?,?,1,strftime('%s','now'))""", (tg_id, enc_string_session))
    c.commit(); c.close()

def get_active_session_enc(tg_id:int):
    c=_conn(); r=c.execute("SELECT string_session FROM sessions WHERE tg_id=? AND active=1 ORDER BY id DESC LIMIT 1",(tg_id,)).fetchone()
    c.close(); return r["string_session"] if r else None

# ----- scheduler/counters -----
def set_running(tg_id:int, on:bool):
    c=_conn(); c.execute("UPDATE schedules SET running=? WHERE tg_id=?",(1 if on else 0, tg_id))
    c.commit(); c.close()

def bump_counters(tg_id:int, is_ad:bool=True):
    c=_conn()
    c.execute("UPDATE counters SET total_sent=total_sent+1, ads_sent=ads_sent+? , last_sent=strftime('%Y-%m-%d %H:%M:%S','now') WHERE tg_id=?",
              (1 if is_ad else 0, tg_id))
    c.commit(); c.close()

# ----- groups by link -----
def groups_count(tg_id:int) -> int:
    c=_conn(); r=c.execute("SELECT COUNT(*) AS n FROM groups WHERE tg_id=?", (tg_id,)).fetchone()
    c.close(); return r["n"] if r else 0

def add_group_link(tg_id:int, link:str, title:str):
    if groups_count(tg_id) >= 5:
        raise ValueError("limit")
    c=_conn()
    c.execute("""INSERT INTO groups(tg_id, peer_id, title, active, last_sent_at, created_at, link)
                 VALUES (?, NULL, ?, 1, NULL, datetime('now','localtime'), ?)""",
              (tg_id, title, link))
    c.commit(); c.close()

def list_groups_links(tg_id:int):
    c=_conn()
    rows=c.execute("""SELECT link, COALESCE(title, link) AS title, last_sent_at
                      FROM groups WHERE tg_id=? ORDER BY id DESC""",(tg_id,)).fetchall()
    c.close(); return rows

def del_group_link(tg_id:int, link:str):
    c=_conn(); c.execute("DELETE FROM groups WHERE tg_id=? AND link=?", (tg_id, link)); c.commit(); c.close()

def mark_group_sent(tg_id:int, peer_id:int):
    c=_conn()
    c.execute("UPDATE groups SET last_sent_at=strftime('%Y-%m-%d %H:%M:%S','now','localtime') WHERE tg_id=? AND (peer_id=? OR peer_id IS NULL)", (tg_id, peer_id))
    c.commit(); c.close()

# ----- ads -----
def add_ad(tg_id:int, msg_link:str, weight:int=1):
    c=_conn(); c.execute("INSERT INTO ads(tg_id,msg_link,weight,active) VALUES (?,?,?,1)",(tg_id,msg_link,weight)); c.commit(); c.close()

def list_ads(tg_id:int):
    c=_conn(); rows=c.execute("SELECT id,msg_link,weight,active FROM ads WHERE tg_id=? ORDER BY id DESC",(tg_id,)).fetchall()
    c.close(); return rows

def del_ad(tg_id:int, ad_id:int):
    c=_conn(); c.execute("DELETE FROM ads WHERE tg_id=? AND id=?", (tg_id, ad_id)); c.commit(); c.close()

def get_ad_by_id(tg_id:int, ad_id:int):
    c=_conn()
    r=c.execute("SELECT id,msg_link,weight,active FROM ads WHERE tg_id=? AND id=?", (tg_id, ad_id)).fetchone()
    c.close(); return r

import random
def pick_weighted_ad(tg_id:int):
    c=_conn()
    rows=c.execute("SELECT id,msg_link,weight FROM ads WHERE tg_id=? AND active=1", (tg_id,)).fetchall()
    c.close()
    if not rows: return None
    pool=[]
    for r in rows:
        w=max(1,int(r["weight"] or 1))
        pool.extend([r]*w)
    return random.choice(pool) if pool else None

# ----- schedule/window -----
def set_interval_minutes(tg_id:int, minutes:int):
    minutes=max(1,int(minutes))
    c=_conn(); c.execute("UPDATE schedules SET interval_sec=? WHERE tg_id=?",(minutes*60,tg_id)); c.commit(); c.close()

def set_window(tg_id:int, start_hhmm:str, end_hhmm:str):
    c=_conn(); c.execute("UPDATE schedules SET window_start=?, window_end=? WHERE tg_id=?",(start_hhmm,end_hhmm,tg_id)); c.commit(); c.close()

# ----- subscriptions -----
def upsert_subscription(tg_id:int, plan:str, days:int):
    now=int(time.time()); until=now + max(1,int(days))*86400
    c=_conn()
    c.execute("""INSERT INTO subs(tg_id,plan,until_ts) VALUES(?,?,?)
                 ON CONFLICT(tg_id) DO UPDATE SET plan=excluded.plan, until_ts=excluded.until_ts""",(tg_id, plan, until))
    c.execute("UPDATE users SET plan=? WHERE tg_id=?", (plan, tg_id))
    c.commit(); c.close(); return until

def get_subscription_status(tg_id:int):
    c=_conn(); r=c.execute("SELECT plan, until_ts FROM subs WHERE tg_id=?", (tg_id,)).fetchone(); c.close()
    plan=r["plan"] if r else "free"; until=r["until_ts"] if r else 0; now=int(time.time())
    left_days=max(0, (until-now)//86400) if until else 0
    active = plan!="free" and until>now
    return {"plan": ("premium" if active else "free"), "until_ts": until, "days_left": left_days}

def redeem_coupon(tg_id:int, code:str):
    c=_conn()
    r=c.execute("SELECT code,plan,days,used_by FROM coupons WHERE code=?", (code,)).fetchone()
    if not r: c.close(); return False, "Invalid code."
    if r["used_by"]: c.close(); return False, "Code already used."
    until = upsert_subscription(tg_id, r["plan"], r["days"])
    c=_conn()
    c.execute("UPDATE coupons SET used_by=?, used_at=strftime('%s','now') WHERE code=?", (tg_id, code))
    c.commit(); c.close()
    return True, "✅ Code applied."

# ----- snapshots -----
def get_account_snapshot(tg_id:int):
    c=_conn()
    ctr  = c.execute("SELECT total_sent, ads_sent, last_sent FROM counters WHERE tg_id=?", (tg_id,)).fetchone()
    sch  = c.execute("SELECT interval_sec, window_start, window_end, running FROM schedules WHERE tg_id=?", (tg_id,)).fetchone()
    c.close()
    return {
        "has_session": has_session(tg_id),
        "sessions":    sessions_count(tg_id),
        "plan":        get_subscription_status(tg_id),
        "counters":    {"total": (ctr["total_sent"] if ctr else 0),
                        "ads":   (ctr["ads_sent"] if ctr else 0),
                        "last":  (ctr["last_sent"] if ctr else "—")},
        "schedule":    {"running": bool(sch and sch["running"]),
                        "interval": int((sch["interval_sec"] or 1200)/60) if sch else 20,
                        "window": f'{sch["window_start"]}-{sch["window_end"]}' if sch else "06:00-12:00"}
    }
    
