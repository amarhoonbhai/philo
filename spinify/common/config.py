# spinify/common/config.py
import os
from pathlib import Path

# --- tokens & usernames ---
MAIN_BOT_TOKEN  = os.getenv("MAIN_BOT_TOKEN", "").strip()
LOGIN_BOT_TOKEN = os.getenv("LOGIN_BOT_TOKEN", "").strip()

MAIN_BOT_USERNAME  = os.getenv("MAIN_BOT_USERNAME", "SpinifyAdsBot").lstrip("@")
LOGIN_BOT_USERNAME = os.getenv("LOGIN_BOT_USERNAME", "SpinifyLoginBot").lstrip("@")

# --- support / contact ---
SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/AnimeLoungeGc").strip()
PREMIUM_CONTACT_USERNAME = os.getenv("PREMIUM_CONTACT_USERNAME", "Spinify").lstrip("@")

# URLs used in menus (safe defaults)
QUICK_GUIDE_URL = os.getenv("QUICK_GUIDE_URL", "https://t.me/PhiloBots").strip()
PREMIUM_URL     = os.getenv("PREMIUM_URL", f"https://t.me/{PREMIUM_CONTACT_USERNAME}").strip()

# --- owner/admin (numeric Telegram user id) ---
try:
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))
except Exception:
    OWNER_ID = 0  # unset

# --- gate / join requirements ---
GATE_PUBLIC_USERNAME  = os.getenv("GATE_PUBLIC_USERNAME", "@PhiloBots").strip()
GATE_PRIVATE_INVITE   = os.getenv("GATE_PRIVATE_INVITE", "").strip()  # invite link for UI
GATE_ENFORCE          = os.getenv("GATE_ENFORCE", "1") == "1"         # 1=enforce, 0=off
# NOTE: private gate chat id is stored in DB key 'gate.private_id' (numeric -100xxxxxxxxxx)

# --- engine / scheduler knobs ---
COOLDOWN_MIN         = int(os.getenv("COOLDOWN_MIN", "20"))     # minutes between sends per target
MAX_PER_TICK         = int(os.getenv("MAX_PER_TICK", "3"))     # messages per scheduler tick
DEFAULT_INTERVAL_MIN = int(os.getenv("DEFAULT_INTERVAL_MIN", "20"))
CYCLE_ON_HOURS       = int(os.getenv("CYCLE_ON_HOURS", "3"))
CYCLE_OFF_HOURS      = int(os.getenv("CYCLE_OFF_HOURS", "1"))

# --- timezone / db ---
TZ = os.getenv("TZ", "Asia/Kolkata")
DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parents[2] / "spinify.sqlite3"))
