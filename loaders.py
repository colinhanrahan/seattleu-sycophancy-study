"""
Load topic text, test messages, and assemble the participant greeting.
"""

import sys
from pathlib import Path

from config import Config


def parse_universal_prompt(config: Config) -> tuple[str, str]:
    prompt_file = Path(config.prompt)
    if not prompt_file.exists():
        sys.exit(f"ERROR: Prompt file not found: {prompt_file}")

    intro, outro = None, None
    for line in prompt_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("INTRO:"):
            intro = line[len("INTRO:"):].strip()
        elif line.startswith("OUTRO:"):
            outro = line[len("OUTRO:"):].strip()

    missing = [k for k, v in (("INTRO", intro), ("OUTRO", outro)) if not v]
    if missing:
        sys.exit(f"ERROR: Missing or empty fields in {prompt_file}: {missing}")

    return intro, outro


def load_topic(config: Config) -> str:
    topic_file = Path(config.topic)
    if not topic_file.exists():
        sys.exit(f"ERROR: Topic file not found: {topic_file}")
    return topic_file.read_text(encoding="utf-8").strip()


def load_test_message(config: Config) -> str | None:
    if not config.test_message:
        return None
    test_file = Path(config.test_message)
    if not test_file.exists():
        sys.exit(f"ERROR: Test message file not found: {test_file}")
    return test_file.read_text(encoding="utf-8").strip()


def build_greeting(config: Config, topic_text: str) -> str:
    """
    Sandwich topic_text between the intro and outro.
    This is shown to the participant only and is not part of the model history.
    """
    intro, outro = parse_universal_prompt(config)
    return f"{intro}\n\n*{topic_text}*\n\n{outro}"
