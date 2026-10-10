# T01 - API key and test call
**Phase A | ~10 min | Depends on: nothing**

## Goal
Have one working LLM key and prove a vision call works, before writing any project code.

## Steps
- [ ] Pick the primary model. Recommended: `gemini-3.1-flash-lite` (free, no card). Backup: `claude-haiku-4-5` if you have credit.
- [ ] Gemini: aistudio.google.com -> Get API key -> Create API key -> Default Gemini Project -> copy.
- [ ] Create `.env` locally (never submit it): `MODEL_PROVIDER`, `MODEL_NAME`, `API_KEY`.
- [ ] Download the Drive folder (https://tinyurl.com/wtq26): 5 training bills.
- [ ] Write a tiny throwaway script: send one bill image + prompt "What is the bill month?" and print the answer.

## Deliverable
A working one-off script and a populated local `.env`.

## Done when
The model returns a sensible answer about a training bill image.

## If stuck
- 401/403: key copied wrong or wrong provider selected.
- 429: wait a minute (free tier is 15 req/min); try the other Gemini model.
- Model name rejected: copy the exact ID from guide section 9.1.
