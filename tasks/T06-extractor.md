# T06 - Extractor
**Phase B | ~15 min | Depends on: T04, T05**

## Goal
Function `extract_level1(image_path) -> dict` returning schema-valid JSON.

## Steps
- [ ] `preprocess.py`: load image, fix EXIF rotation, convert to RGB, downscale if very large (keep text readable).
- [ ] `extractor.py`: call `llm_client.generate` with prompt + image; parse JSON (strip code fences); validate with pydantic.
- [ ] On parse/validation failure: one retry that includes the error message.
- [ ] If still failing: return a safe object with all fields present (`null`/`[]`) and log a warning (never crash).
- [ ] Never include identifiers (extra safety: drop unknown keys).

## Deliverable
`extractor.py`, `preprocess.py`.

## Done when
Running on `KESC_0008.png` returns JSON that parses and looks close to the expected one.
