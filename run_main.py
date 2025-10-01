#!/usr/bin/env python3
import sys, os
from pathlib import Path

def _load_env():
    for p in (Path.cwd() / ".env", Path("/opt/spinify/.env")):
        if p.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(p, override=True)
            except Exception:
                pass

_load_env()

from aiogram.utils.token import validate_token
from spinify.common.config import MAIN_BOT_TOKEN

import asyncio
from spinify.main_bot.main import main as mainbot_main

def _ensure_token():
    try:
        validate_token(MAIN_BOT_TOKEN)
    except Exception:
        sys.stderr.write(
            "[run_main] MAIN_BOT_TOKEN missing/invalid in environment.\n"
            "  set it like: export MAIN_BOT_TOKEN=1234567890:AA...  and re-run\n"
        )
        sys.exit(1)

if __name__ == "__main__":
    _ensure_token()
    asyncio.run(mainbot_main())
