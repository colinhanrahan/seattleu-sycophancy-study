# Sycophancy study backend

A Chainlit-based chat interface for running human subjects research on LLM sycophancy. Participants are given a topic prompt and chat with a locally-hosted open-source model (will be `gpt-oss:20b` or possibly `gpt-oss:120b`, but `qwen2.5:3b` is currently used for local testing). Sessions are logged in both .jsonl and human-readable .md files.

## Requirements
- Python 3.12+
- Ollama installed on the server with the model already downloaded
  - [Linux installation instructions](https://docs.ollama.com/linux)

## Quickstart
```bash
# 1. Clone and set up
git clone <repo-url> && cd <repo>
python3 -m venv venv
source venv/bin/activate
make install

# 2. Configure
# Edit config.yaml to set server_url, model, and participant_id

# 3. Run
make run
```
The app opens in the browser at http://localhost:8000.

## Make Commands

```bash
make install     # install Python dependencies
make run         # run the experiment (reads from config.yaml)
make clean       # delete all session logs (asks for confirmation)
```

## Configuration

All configuration lives in `config.yaml`. At minimum, edit `participant_id` before each session.

| Field | Description |
|---|---|
| `participant_id` | Unique participant ID |
| `model` | Model name as known to Ollama, e.g. `qwen2.5:3b`, `gpt-oss:20b` |
| `server_url` | Ollama API base URL (default: `http://localhost:11434/v1`) |
| `dry_run` | If `true`, run without saving any logs (default: `false`) |
| `human_readable` | If `false`, skip the `.txt` log alongside `.jsonl` (default: `true`) |
| `prompt` | Path to intro prompt excluding topic (default: `prompts/universal.txt`) |
| `test_message` | Auto-send a first message, e.g. `test_messages/food_desert/positive.txt` (default: `null`) |
| `topic` | Path to topic (default: `topics/food_desert.txt`) |
