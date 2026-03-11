"""
Chainlit app entry point for the sycophancy study.
This file contains only the Chainlit lifecycle hooks.

Run with:
    python -m chainlit run chat_session.py
Or just:
    make run

See README.md for full usage. Edit config.yaml before running.
"""

import os
import asyncio
import signal
import time
from pathlib import Path

import chainlit as cl
from openai import OpenAI

from config import load_config
from loaders import load_topic, load_test_message, build_greeting
from session_logger import elapsed, get_log_stem, append_jsonl, append_readable


CONFIG = load_config()
client = OpenAI(base_url=CONFIG.server_url, api_key="not-needed")
TOPIC_TEXT = load_topic(CONFIG)
TEST_MESSAGE = load_test_message(CONFIG)
GREETING = build_greeting(CONFIG, TOPIC_TEXT)
END_PHRASES = {"end", "end chat", "end conversation", "stop", "quit", "exit"}


async def end_session(reason: str) -> None:
    """Write session_end to logs, show farewell message, then exit the process."""
    cl.user_session.set("session_ended", True)

    log_path: Path | None = cl.user_session.get("log_path")
    md_path: Path | None = cl.user_session.get("md_path")
    start_time: float = cl.user_session.get("start_time")

    farewell = "Your session has ended. Thank you for participating! You may close this window."

    if log_path:
        ts = elapsed(start_time)
        append_jsonl(CONFIG, log_path, {
            "event": "session_end",
            "participant_id": CONFIG.participant_id,
            "reason": reason,
            "elapsed": ts,
        })
        append_readable(CONFIG, md_path, "system", ts, farewell)
        if CONFIG.dry_run:
            print("[DRY RUN] Session ended, no logs saved.")
        else:
            print(f"[INFO] Session ended ({reason}). JSONL: {log_path}")
            if CONFIG.human_readable and md_path:
                print(f"[INFO] Text log: {md_path}")
    else:
        print("[INFO] Session ended before any messages, no log created.")

    await cl.Message(content=farewell).send()
    await asyncio.sleep(0.5)
    os.kill(os.getpid(), signal.SIGTERM)


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("conversation_history", [])
    cl.user_session.set("log_path", None)
    cl.user_session.set("md_path", None)
    cl.user_session.set("session_ended", False)
    cl.user_session.set("start_time", time.monotonic())

    if CONFIG.dry_run:
        print("[DRY RUN] Logging disabled.")

    await cl.Message(content=GREETING).send()

    if TEST_MESSAGE:
        await cl.Message(content=TEST_MESSAGE, type="user_message").send()
        await on_message(cl.Message(content=TEST_MESSAGE))


@cl.on_message
async def on_message(message: cl.Message):
    if cl.user_session.get("session_ended"):
        return

    log_path: Path | None = cl.user_session.get("log_path")
    md_path: Path | None = cl.user_session.get("md_path")
    history: list = cl.user_session.get("conversation_history")
    start_time: float = cl.user_session.get("start_time")
    text = message.content.strip()
    ts = elapsed(start_time)

    if text.lower() in END_PHRASES:
        if log_path:
            append_jsonl(CONFIG, log_path, {
                "event": "user_message",
                "participant_id": CONFIG.participant_id,
                "elapsed": ts,
                "content": text,
            })
            append_readable(CONFIG, md_path, "user", ts, text)
        await end_session(reason="user_ended_chat")
        return

    if log_path is None:
        log_path, md_path = get_log_stem(CONFIG)
        cl.user_session.set("log_path", log_path)
        cl.user_session.set("md_path", md_path)

        append_jsonl(CONFIG, log_path, {
            "event": "session_start",
            "participant_id": CONFIG.participant_id,
            "model": CONFIG.model,
            "server_url": CONFIG.server_url,
            "log_file": str(log_path),
            "elapsed": "00:00",
        })
        append_jsonl(CONFIG, log_path, {
            "event": "participant_prompt",
            "elapsed": "00:00",
            "topic": TOPIC_TEXT,
            "full_prompt": GREETING,
            "note": "shown to participant only — not in model conversation history",
        })
        append_readable(CONFIG, md_path, "prompt", "00:00", GREETING)

        print(f"[INFO] Participant: {CONFIG.participant_id}")
        print(f"[INFO] Model:       {CONFIG.model}")

    history.append({"role": "user", "content": text})
    user_entry = {
        "event": "user_message",
        "participant_id": CONFIG.participant_id,
        "elapsed": ts,
        "content": text,
    }
    if TEST_MESSAGE and text == TEST_MESSAGE:
        user_entry["note"] = "auto-sent test message"
    append_jsonl(CONFIG, log_path, user_entry)
    append_readable(CONFIG, md_path, "user", ts, text)

    response_message = cl.Message(content="")
    await response_message.send()

    full_reply = ""
    try:
        stream = client.chat.completions.create(
            model=CONFIG.model,
            messages=history,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_reply += delta
            await response_message.stream_token(delta)

    except Exception as e:
        error_text = f"Error communicating with the model: {e}"
        await response_message.stream_token(f"\n\n{error_text}")
        append_jsonl(CONFIG, log_path, {
            "event": "error",
            "elapsed": elapsed(start_time),
            "error": str(e),
        })

    await response_message.update()

    reply_ts = elapsed(start_time)
    history.append({"role": "assistant", "content": full_reply})
    cl.user_session.set("conversation_history", history)

    append_jsonl(CONFIG, log_path, {
        "event": "assistant_message",
        "participant_id": CONFIG.participant_id,
        "model": CONFIG.model,
        "elapsed": reply_ts,
        "content": full_reply,
    })
    append_readable(CONFIG, md_path, "assistant", reply_ts, full_reply)
