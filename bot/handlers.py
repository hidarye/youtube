import os
import traceback
from typing import Optional

from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import Message

from .config import Settings
from .downloader import is_url, download_video, run_in_thread


def format_bytes(num_bytes: Optional[int]) -> str:
    if not num_bytes:
        return "?"
    units = ["B", "KB", "MB", "GB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} GB"


def register_handlers(app: Client, settings: Settings) -> None:
    @app.on_message(filters.command(["start", "help"]) & ~filters.edited)
    async def start_handler(client: Client, message: Message):
        await message.reply_text(
            "أرسل رابط فيديو (YouTube, TikTok, Instagram, Twitter, ...).\n"
            "سأقوم بتحميله وإرساله لك.\n"
            "يمكن ضبط الحد الأقصى للحجم عبر المتغير MAX_FILE_SIZE_MB."
        )

    @app.on_message(filters.text & ~filters.command(["start", "help"]))
    async def url_handler(client: Client, message: Message):
        text = message.text.strip()
        if not is_url(text):
            return

        status = await message.reply_text("جاري التحميل... ⏳")
        try:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)

            result = await run_in_thread(
                download_video,
                text,
                settings.download_dir,
                settings.max_file_size_mb,
                None,
            )

            caption = f"{result.title}"
            if result.duration:
                mins = result.duration // 60
                secs = result.duration % 60
                caption += f"\n⏱ {mins}:{secs:02d}"
            if result.filesize:
                caption += f"\n💾 {format_bytes(result.filesize)}"
            if result.webpage_url:
                caption += f"\n🔗 {result.webpage_url}"

            await status.edit_text("جاري الرفع... ⏫")
            await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

            file_path = result.filepath
            send_kwargs = dict(
                chat_id=message.chat.id,
                caption=caption,
            )

            if result.ext.lower() in {"mp4", "mkv", "webm", "mov", "avi"}:
                await client.send_video(video=file_path, supports_streaming=True, **send_kwargs)
            else:
                await client.send_document(document=file_path, **send_kwargs)

            await status.edit_text("تم الإرسال ✅")
        except Exception:
            await status.edit_text("حدث خطأ أثناء التحميل أو الإرسال. ❌")
            print(traceback.format_exc())
        finally:
            try:
                if 'result' in locals() and os.path.exists(result.filepath):
                    os.remove(result.filepath)
            except Exception:
                pass