# T12 - Dry run on training bills
**Phase D | ~10 min | Depends on: T11**

## Goal
Rehearse test day with the 5 training bills so nothing surprises you at 12:30.

## Steps
- [ ] Build fake templates: `level1.csv` with 5 rows, `level2.csv` with 5 x 12 rows using your own 12 sample questions.
- [ ] Run the full command exactly as you will on test day.
- [ ] Time it. Expected total should be a few minutes. If slow, raise `--workers` carefully (watch rate limits).
- [ ] Inspect output manually: pick 2 bills and compare to the images.
- [ ] Clear cache and run once more from scratch to confirm a clean environment works.

## Done when
Complete run with zero crashes and plausible outputs.
