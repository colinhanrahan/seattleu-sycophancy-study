import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Config:
    participant_id: str
    model: str
    server_url: str
    dry_run: bool
    human_readable: bool
    test_message: str | None
    topic: str
    prompt: str


def load_config(path: str = "config.yaml") -> Config:
    cfg_file = Path(path)
    if not cfg_file.exists():
        sys.exit(f"ERROR: Config file not found: {path}")

    with cfg_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return Config(
        participant_id=str(data["participant_id"]).strip(),
        model=str(data["model"]).strip(),
        server_url=data["server_url"],
        dry_run=bool(data["dry_run"]),
        human_readable=bool(data["human_readable"]),
        test_message=data.get("test_message") or None,
        topic=data["topic"],
        prompt=data["prompt"],
    )
