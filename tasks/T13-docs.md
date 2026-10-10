# T13 - README, .env.example, requirements
**Phase E | ~15 min | Depends on: T11 (can be drafted earlier)**

## Steps
- [ ] `README.md` must include:
  - what the project does (2-3 lines) and architecture diagram (from plan.md)
  - Python version (e.g. "Python 3.12")
  - setup: venv, `pip install -r requirements.txt`, copy `.env.example` to `.env`, add API key
  - exact run command for a folder of bills + templates, expected outputs
  - design choices (vision LLM, validation, code-based calculations, caching, fallbacks)
  - **AI usage section**: models/APIs used (must match code), services used, AI tools used to write the code (Claude, etc.); write "none" for unused categories
  - known limitations
- [ ] `.env.example` with real non-secret values and placeholder key:
  ```
  MODEL_PROVIDER=google
  MODEL_NAME=gemini-3.1-flash-lite
  API_KEY=your-api-key-here
  ```
- [ ] `requirements.txt` with `package==x.y.z`.
- [ ] Confirm every env var read in code appears in `.env.example`.

## Done when
A teammate could run the project from the README alone.
