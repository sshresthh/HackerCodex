import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def dated_filename(prefix: str, ext: str = "json") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}.{ext}"


def source_paths(source_key: str, ext: str = "json") -> tuple[str, str]:
    """
    Returns (dated_path, latest_path) for a source.
    Example: (data/eventbrite/eventbrite_20250101T010000Z.json, data/eventbrite/latest.json)
    """
    src_dir = os.path.join(DATA_DIR, source_key)
    ensure_dir(src_dir)
    dated = os.path.join(src_dir, dated_filename(source_key, ext))
    latest = os.path.join(src_dir, f"latest.{ext}")
    return dated, latest


