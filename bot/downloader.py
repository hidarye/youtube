import asyncio
import os
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

import yt_dlp


@dataclass
class DownloadResult:
    filepath: str
    title: str
    ext: str
    duration: Optional[int]
    filesize: Optional[int]
    webpage_url: Optional[str]


_URL_REGEX = re.compile(r"https?://\S+", re.IGNORECASE)


def is_url(text: str) -> bool:
    return bool(_URL_REGEX.search(text or ""))


def _build_basic_ydl_opts(download_dir: str, progress_hook) -> Dict[str, Any]:
    return {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "trim_file_name": 200,
        "outtmpl": os.path.join(download_dir, "%(title).150s [%(id)s].%(ext)s"),
        "restrictfilenames": False,
        "noplaylist": True,
        "concurrent_fragment_downloads": 4,
        "retries": 10,
        "fragment_retries": 10,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118 Safari/537.36",
        },
        "progress_hooks": [progress_hook] if progress_hook else [],
    }


def _format_candidates(max_mb: int) -> List[str]:
    size_limit = f"{max_mb}M"
    return [
        f"(bv*[ext=mp4][height<=1080]+ba[ext=m4a]/b[ext=mp4][height<=1080])[filesize?<=${size_limit}][filesize_approx?<=${size_limit}]".replace("$", ""),
        f"(bv*[ext=mp4][height<=720]+ba[ext=m4a]/b[ext=mp4][height<=720])[filesize?<=${size_limit}][filesize_approx?<=${size_limit}]".replace("$", ""),
        f"(bv*[ext=mp4][height<=480]+ba[ext=m4a]/b[ext=mp4][height<=480])[filesize?<=${size_limit}][filesize_approx?<=${size_limit}]".replace("$", ""),
        f"b[filesize?<=${size_limit}][filesize_approx?<=${size_limit}]".replace("$", ""),
        "bv*+ba/b",
    ]


def _try_download(url: str, ydl_opts: Dict[str, Any]) -> Dict[str, Any]:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if "requested_downloads" in info:
            entry = info["requested_downloads"][0]
            filepath = entry.get("_filename") or ydl.prepare_filename(info)
        else:
            filepath = ydl.prepare_filename(info)
        return {"info": info, "filepath": filepath}


def download_video(url: str, download_dir: str, max_file_size_mb: int, progress_hook=None) -> DownloadResult:
    last_error: Optional[Exception] = None
    ydl_base = _build_basic_ydl_opts(download_dir, progress_hook)

    for fmt in _format_candidates(max_file_size_mb):
        ydl_opts = {**ydl_base, "format": fmt}
        try:
            result = _try_download(url, ydl_opts)
            info = result["info"]
            filepath = result["filepath"]
            if not os.path.exists(filepath):
                alt_path = ydl_opts.get("outtmpl", "")
                if alt_path and os.path.exists(alt_path):
                    filepath = alt_path
            size_bytes = os.path.getsize(filepath) if os.path.exists(filepath) else None
            if size_bytes and size_bytes > max_file_size_mb * 1024 * 1024:
                try:
                    os.remove(filepath)
                except Exception:
                    pass
                last_error = RuntimeError("Downloaded file exceeds size limit; trying lower quality.")
                continue

            return DownloadResult(
                filepath=filepath,
                title=info.get("title") or os.path.basename(filepath),
                ext=os.path.splitext(filepath)[1].lstrip("."),
                duration=info.get("duration"),
                filesize=size_bytes,
                webpage_url=info.get("webpage_url"),
            )
        except Exception as exc:
            last_error = exc
            continue

    raise RuntimeError(f"Could not download video within size limit: {last_error}")


async def run_in_thread(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))