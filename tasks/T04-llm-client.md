# T04 - LLM client abstraction
**Phase B | ~15 min | Depends on: T02**

## Goal
One function that works for any allowed provider, with retries and caching.

## Steps
- [ ] `llm_client.py`: `generate(prompt, image_path=None, json_schema=None, system=None) -> str`.
- [ ] Implement provider branches for `google`, `anthropic`, `openai` (at least the one you use; others can be thin).
- [ ] Ask for JSON output (native structured output where supported, else "return only JSON").
- [ ] Retry with exponential backoff on 429 / 5xx / timeouts (max 4 tries).
- [ ] Cache: key = hash(model + prompt + image bytes); store response in `cache/`. Reruns cost nothing.
- [ ] Only allowed model IDs accepted; raise an error for any other (protects against accidental disqualification).
- [ ] Set temperature to 0 (or lowest allowed) for deterministic extraction.

## Deliverable
`llm_client.py` with a small unit test using a mocked SDK.

## Done when
Calling `generate` twice with the same input hits the network only once.

## If stuck
Some models restrict temperature or JSON mode; check the provider docs and fall back to "JSON only" prompting plus pydantic validation.
