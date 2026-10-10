# T02 - Project skeleton and config
**Phase A | ~15 min | Depends on: T01**

## Goal
Create the folder structure and config loading so every later task has a home.

## Steps
- [ ] Create the structure from `plan.md` section 6.
- [ ] Create venv with Python 3.11+ (`python --version`), note the exact version.
- [ ] Install libs: `python-dotenv`, `pydantic`, `Pillow`, and the SDK for your provider (`google-genai`, `anthropic` or `openai`). Add `pytest`.
- [ ] `config.py`: load `MODEL_PROVIDER`, `MODEL_NAME`, `API_KEY` (plus optional `MAX_WORKERS`, `CACHE_DIR`) from env; fail with a clear message if missing.
- [ ] `.gitignore`: `.env`, `cache/`, `__pycache__/`, `.venv/`, `data/`.
- [ ] `pip freeze` to `requirements.txt` (exact `==` versions; trim to direct dependencies).

## Deliverable
Skeleton repo where `python -c "from bill_decoder.config import load_config; print(load_config())"` works (without printing the key).

## Done when
Imports work and missing env vars give a friendly error.
