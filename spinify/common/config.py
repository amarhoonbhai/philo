import os

MAIN_BOT_TOKEN  = os.getenv("MAIN_BOT_TOKEN", "")
LOGIN_BOT_TOKEN = os.getenv("LOGIN_BOT_TOKEN", "")
LOGIN_BOT_USERNAME = os.getenv("LOGIN_BOT_USERNAME", "SpinifyLoginBot")

QUICK_GUIDE_URL = os.getenv("QUICK_GUIDE_URL", "https://t.me/TheTrafficZone")
PREMIUM_URL     = os.getenv("PREMIUM_URL", "https://t.me/PhiloBots")

GATE_PUBLIC_USERNAME = os.getenv("GATE_PUBLIC_USERNAME", "@PhiloBots")
GATE_PRIVATE_INVITE  = os.getenv("GATE_PRIVATE_INVITE", "https://t.me/+X83tuZcK0FkwZWY1")

OWNER_ID = int(os.getenv("OWNER_ID", "5365568568"))
DB_PATH  = os.getenv("DB_PATH", "spinify.sqlite3")
