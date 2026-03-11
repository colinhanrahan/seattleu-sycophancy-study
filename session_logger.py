"""
File I/O for session logging.

Produces two files per session in logs/<participant_id>_logs/:
  - <participant_id>_log_N.jsonl
  - <participant_id>_log_N.md
"""

import json
import time
from pathlib import Path

from config import Config


def elapsed(start: float) -> str:
    secs = int(time.monotonic() - start)
    return f"{secs // 60:02d}:{secs % 60:02d}"


def get_log_stem(config: Config) -> tuple[Path, Path]:
    """Return (jsonl_path, md_path) for the next available session index."""
    log_dir = Path(f"logs/{config.participant_id}_logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    index = 1
    while True:
        stem = log_dir / f"{config.participant_id}_log_{index}"
        if not stem.with_suffix(".jsonl").exists():
            return stem.with_suffix(".jsonl"), stem.with_suffix(".md")
        index += 1


def append_jsonl(config: Config, log_path: Path, entry: dict) -> None:
    if config.dry_run:
        return
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def append_readable(config: Config, md_path: Path, role: str, timestamp: str, content: str) -> None:
    if config.dry_run or not config.human_readable:
        return
    with md_path.open("a", encoding="utf-8") as f:
        f.write(f"### `{role.upper()} [{timestamp}]`\n\n")
        f.write(content + "\n\n")
        f.write("---\n\n")
