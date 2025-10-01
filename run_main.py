#!/usr/bin/env python3
import os, sys, re, asyncio

# Hard fail if the token isn't present/valid
def require_token(name: str, value: str):
    if not value or not re.fullmatch(r"\d+:[\w\-]{30,}", value):
        sys.stderr.write(
            f"[run_main] {name} missing/invalid in environment.\n"
            f"  set it like: export {name}=1234567890:AA...  and re-run\n"
        )
        sys.exit(2)

def main_entry():
    # optional: quiet tzlocal warning and set consistent tz
    os.environ.setdefault("TZ", os.getenv("TZ", "Asia/Kolkata"))

    # read token from ENV (config.py also pulls from env, but we validate early here)
    from spinify.common.config import MAIN_BOT_TOKEN
    require_token("MAIN_BOT_TOKEN", MAIN_BOT_TOKEN)

    # run the bot
    from spinify.main_bot.main import main
    asyncio.run(main())

if __name__ == "__main__":
    main_entry()
