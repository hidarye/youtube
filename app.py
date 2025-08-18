import logging
import sys

try:
    import uvloop  # type: ignore
    uvloop.install()
except Exception:
    pass

from pyrogram import Client

from bot.config import load_settings
from bot.handlers import register_handlers


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("bot.log", encoding="utf-8"),
        ],
    )


def create_client() -> Client:
    settings = load_settings()

    if settings.bot_token and settings.session_string:
        raise RuntimeError("Provide only one of BOT_TOKEN or SESSION_STRING, not both.")

    if not settings.bot_token and not settings.session_string:
        raise RuntimeError("You must set either BOT_TOKEN for bot mode or SESSION_STRING for user mode.")

    if settings.bot_token:
        app = Client(
            name="bot",
            api_id=settings.api_id,
            api_hash=settings.api_hash,
            bot_token=settings.bot_token,
            workdir=".",
            in_memory=False,
        )
    else:
        # Prefer session_string parameter; fallback to StringSession for compatibility
        try:
            app = Client(
                name="user",
                api_id=settings.api_id,
                api_hash=settings.api_hash,
                session_string=settings.session_string,
                workdir=".",
                in_memory=False,
            )
        except TypeError:
            from pyrogram.session import StringSession  # type: ignore

            app = Client(
                name=StringSession(settings.session_string),  # type: ignore
                api_id=settings.api_id,
                api_hash=settings.api_hash,
                workdir=".",
                in_memory=False,
            )

    register_handlers(app, settings)
    return app


if __name__ == "__main__":
    setup_logging()
    app = create_client()
    app.run()