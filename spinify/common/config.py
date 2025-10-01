import os

def _env_str(k, d=""):
    return os.getenv(k, d)

def _env_int(k, d=0):
    try:
        return int(os.getenv(k, str(d)))
    except Exception:
        return d

# --- Tokens & usernames ---
MAIN_BOT_TOKEN      = _env_str("MAIN_BOT_TOKEN", "")
LOGIN_BOT_TOKEN     = _env_str("LOGIN_BOT_TOKEN", "")
LOGIN_BOT_USERNAME  = _env_str("LOGIN_BOT_USERNAME", "SpinifyLoginBot")
MAIN_BOT_USERNAME   = _env_str("MAIN_BOT_USERNAME", "SpinifyAdsBot")

# --- Links & UX ---
QUICK_GUIDE_URL     = _env_str("QUICK_GUIDE_URL", "https://t.me/TheTrafficZone")
PREMIUM_URL         = _env_str("PREMIUM_URL", "https://t.me/PhiloBots")
SUPPORT_URL         = _env_str("SUPPORT_URL", "https://t.me/AnimeLoungeGc")

# Premium contact
PREMIUM_CONTACT_USERNAME = _env_str("PREMIUM_CONTACT_USERNAME", "Spinify")
PREMIUM_CONTACT_URL = f"https://t.me/{PREMIUM_CONTACT_USERNAME}"

# Gate (public channel & private GC)
GATE_PUBLIC_USERNAME = _env_str("GATE_PUBLIC_USERNAME", "@PhiloBots")
GATE_PRIVATE_INVITE  = _env_str("GATE_PRIVATE_INVITE", "https://t.me/+X83tuZcK0FkwZWY1")

# Owner & storage
OWNER_ID            = _env_int("OWNER_ID", 5365568568)
DB_PATH             = _env_str("DB_PATH", "spinify.sqlite3")
ENCRYPT_KEY         = _env_str("ENCRYPT_KEY", "")
TZ                  = _env_str("TZ", "Asia/Kolkata")

# Ads engine knobs
COOLDOWN_MIN = _env_int("COOLDOWN_MIN", 45)  # minutes between sends per group
MAX_PER_TICK = _env_int("MAX_PER_TICK", 3)   # how many groups to hit per scheduler tick
