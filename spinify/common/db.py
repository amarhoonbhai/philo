import sqlite3
from pathlib import Path
from .config import DB_PATH

Path(DB_PATH).touch(exist_ok=True)

def _conn():
    c = sqlite3.connect(DB_PATH); c.row_factory = sqlite3.Row; return c

def init_core():
    c = _conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(tg_id INTEGER PRIMARY KEY, plan TEXT DEFAULT 'free');
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
    CREATE TABLE IF NOT EXISTS gates(tg_id INTEGER PRIMARY KEY, agreed_tos INTEGER DEFAULT 0);
    """); c.commit(); c.close()

def init_bot_tables():
    c = _conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS sessions(
      id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id INTEGER, string_session TEXT, active INTEGER DEFAULT 1, created_at INTEGER
    );
    CREATE TABLE IF NOT EXISTS groups(
      id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id INTEGER, peer_id INTEGER, title TEXT, active INTEGER DEFAULT 1, last_sent_at TEXT
    );
    CREATE TABLE IF NOT EXISTS ads(
      id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id INTEGER, msg_link TEXT, weight INTEGER DEFAULT 1, active INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS schedules(
      tg_id INTEGER PRIMARY KEY, interval_sec INTEGER DEFAULT 1200, window_start TEXT DEFAULT '06:00', window_end TEXT DEFAULT '12:00', running INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS counters(
      tg_id INTEGER PRIMARY KEY, total_sent INTEGER DEFAULT 0, ads_sent INTEGER DEFAULT 0, last_sent TEXT
    );
    """)
    c.execute("INSERT OR IGNORE INTO schedules(tg_id) SELECT tg_id FROM users;")
    c.execute("INSERT OR IGNORE INTO counters(tg_id)  SELECT tg_id FROM users;")
    c.commit(); c.close()

def ensure_user(tg_id:int):
    c=_conn()
    c.execute("INSERT OR IGNORE INTO users(tg_id) VALUES(?)",(tg_id,))
    c.execute("INSERT OR IGNORE INTO gates(tg_id) VALUES(?)",(tg_id,))
    c.execute("INSERT OR IGNORE INTO schedules(tg_id) VALUES(?)",(tg_id,))
    c.execute("INSERT OR IGNORE INTO counters(tg_id)  VALUES(?)",(tg_id,))
    c.commit(); c.close()

def set_setting(k,v):
    c=_conn(); c.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(k,v)); c.commit(); c.close()
def get_setting(k):
    c=_conn(); r=c.execute("SELECT value FROM settings WHERE key=?",(k,)).fetchone(); c.close(); return r["value"] if r else None

def set_agreed(tg_id,yes): c=_conn(); c.execute("UPDATE gates SET agreed_tos=? WHERE tg_id=?",(1 if yes else 0,tg_id)); c.commit(); c.close()
def agreed(tg_id): c=_conn(); r=c.execute("SELECT agreed_tos FROM gates WHERE tg_id=?",(tg_id,)).fetchone(); c.close(); return bool(r and r["agreed_tos"])

def has_session(tg_id:int)->bool:
    c=_conn(); r=c.execute("SELECT 1 FROM sessions WHERE tg_id=? AND active=1 LIMIT 1",(tg_id,)).fetchone(); c.close(); return bool(r)

def set_running(tg_id:int, on:bool):
    c=_conn(); c.execute("UPDATE schedules SET running=? WHERE tg_id=?",(1 if on else 0, tg_id)); c.commit(); c.close()
