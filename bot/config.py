import os
import logging
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    api_id: int
    api_hash: str
    bot_token: Optional[str]
    session_string: Optional[str]
    download_dir: str
    max_file_size_mb: int
    owner_id: Optional[int]


def load_settings() -> Settings:
    load_dotenv()

    api_id_str = os.getenv("API_ID", "").strip()
    api_hash = os.getenv("API_HASH", "").strip()
    bot_token = os.getenv("BOT_TOKEN", "").strip() or None
    session_string = os.getenv("SESSION_STRING", "").strip() or None
    download_dir = os.getenv("DOWNLOAD_DIR", "downloads").strip() or "downloads"
    max_file_size_mb_str = os.getenv("MAX_FILE_SIZE_MB", "1900").strip()
    owner_id_str = os.getenv("OWNER_ID", "").strip()

    if not api_id_str or not api_hash:
        raise RuntimeError("API_ID and API_HASH must be set in environment.")

    try:
        api_id = int(api_id_str)
    except ValueError as exc:
        raise RuntimeError("API_ID must be an integer.") from exc

    try:
        max_file_size_mb = int(max_file_size_mb_str)
    except ValueError as exc:
        raise RuntimeError("MAX_FILE_SIZE_MB must be an integer.") from exc

    owner_id: Optional[int] = None
    if owner_id_str:
        try:
            owner_id = int(owner_id_str)
        except ValueError:
            logging.warning("OWNER_ID must be an integer; ignoring invalid value.")

    os.makedirs(download_dir, exist_ok=True)

    return Settings(
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token,
        session_string=session_string,
        download_dir=download_dir,
        max_file_size_mb=max_file_size_mb,
        owner_id=owner_id,
    )