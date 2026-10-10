# T14 - Code freeze and packaging script
**Phase E | ~10 min | Depends on: T12, T13**

## Goal
Make packaging a one-command, repeatable, safe step.

## Steps
- [ ] `scripts/package.py` (or shell script) that builds `submission.zip` with:
  ```
  output/level1.csv
  output/level2.csv
  source/  (code, README.md, .env.example, requirements.txt, tests)
  demo/demo.mp4   (only if it exists)
  ```
- [ ] Exclude: `.env`, `.venv`, `cache/`, `__pycache__`, `data/`, `.git`, large files.
- [ ] Script prints ZIP size and fails if > 15 MB.
- [ ] Script greps for key-like strings (`AIza`, `sk-`, `API_KEY=` with real value) and aborts if found.
- [ ] Commit/tag the code at **12:30** (code freeze).

## Done when
Dry-run ZIP from T12 opens with the right structure and no secrets.
