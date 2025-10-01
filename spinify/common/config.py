# spinify/common/config.py
import os
from pathlib import Path

# --- tokens & usernames ---
MAIN_BOT_TOKEN  = os.getenv("MAIN_BOT_TOKEN", "").strip()
LOGIN_BOT_TOKEN = os.getenv("LOGIN_BOT_TOKEN", "").strip()

MAIN_BOT_USERNAME  = os.getenv("MAIN_BOT_USERNAME", "SpinifyAdsBot").lstrip("@")
LOGIN_BOT_USERNAME = os.getenv("LOGIN_BOT_USERNAME", "SpinifyLoginBot").lstrip("@")

# --- links & support ---
SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/AnimeLoungeGc").strip()
PREMIUM_CONTACT_USERNAME = os.getenv("PREMIUM_CONTACT_USERNAME", "Spinify").lstrip("@")

# --- gating / enforcement ---
# Public channel username (with or without '@')
GATE_PUBLIC_USERNAME = os.getenv("GATE_PUBLIC_USERNAME", "@PhiloBots").strip()
# Quick on/off switch for enforcement (set GATE_ENFORCE=0 in /opt/spinify/.env while testing)
GATE_ENFORCE = os.getenv("GATE_ENFORCE", "1") == "1"
# Private gate chat id is stored in DB settings key: gate.private_id (numeric -100xxxxxxxxxx)

# --- engine knobs / scheduling (defaults are safe; override in .env if needed) ---
COOLDOWN_MIN        = int(os.getenv("COOLDOWN_MIN",        "20"))   # minutes between sends to the same target
MAX_PER_TICK        = int(os.getenv("MAX_PER_TICK",        "3"))   # max messages to send per scheduler tick
DEFAULT_INTERVAL_MIN= int(os.getenv("DEFAULT_INTERVAL_MIN","20"))  # default user interval 20m
CYCLE_ON_HOURS      = int(os.getenv("CYCLE_ON_HOURS",      "3"))   # run window: 3h ON
CYCLE_OFF_HOURS     = int(os.getenv("CYCLE_OFF_HOURS",     "1"))   # then 1h OFF

# --- timezone ---
TZ = os.getenv("TZ", "Asia/Kolkata")

# --- database path ---
DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parents[2] / "spinify.sqlite3"))
