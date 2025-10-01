#!/usr/bin/env python3
import os, sys, re, asyncio

def require_token(name: str, value: str):
    if not value or not re.fullmatch(r"\d+:[\w\-]{30,}", value):
        sys.stderr.write(
            f"[run_login] {name} missing/invalid in environment.\n"
            f"  set it like: export {name}=1234567890:AA...  and re-run\n"
        )
        sys.exit(2)

def main_entry():
    os.environ.setdefault("TZ", os.getenv("TZ", "Asia/Kolkata"))

    from spinify.common.config import LOGIN_BOT_TOKEN
    require_token("LOGIN_BOT_TOKEN", LOGIN_BOT_TOKEN)

    from spinify.login_bot.main import main
    asyncio.run(main())

if __name__ == "__main__":
    main_entry()
