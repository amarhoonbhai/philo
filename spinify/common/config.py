# spinify/common/config.py
import os
from pathlib import Path

# --- tokens & usernames ---
MAIN_BOT_TOKEN  = os.getenv("MAIN_BOT_TOKEN", "").strip()
LOGIN_BOT_TOKEN = os.getenv("LOGIN_BOT_TOKEN", "").strip()

MAIN_BOT_USERNAME  = os.getenv("MAIN_BOT_USERNAME", "SpinifyAdsBot").lstrip("@")
LOGIN_BOT_USERNAME = os.getenv("LOGIN_BOT_USERNAME", "SpinifyLoginBot").lstrip("@")

SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/AnimeLoungeGc").strip()
PREMIUM_CONTACT_USERNAME = os.getenv("PREMIUM_CONTACT_USERNAME", "Spinify").lstrip("@")

# --- gating / enforcement ---
# Public channel username (with or without '@' is fine)
GATE_PUBLIC_USERNAME = os.getenv("GATE_PUBLIC_USERNAME", "@PhiloBots").strip()

# Enable/disable enforcement quickly for testing (0 = off, 1 = on)
GATE_ENFORCE = os.getenv("GATE_ENFORCE", "1") == "1"

# Private gate chat id is stored in DB settings key: gate.private_id (numeric -100xxxx)
# (Use: sqlite3 spinify.sqlite3 "INSERT INTO settings(key,value) VALUES('gate.private_id','-1001234567890') ON CONFLICT(key) DO UPDATE SET value=excluded.value;")

# --- database path ---
DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parents[2] / "spinify.sqlite3"))
