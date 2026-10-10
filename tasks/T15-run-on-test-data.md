# T15 - Run on test data
**Phase F | 12:30 | ~20 min | Depends on: T14**

## Steps
- [ ] Download `test/bills/` (10 images) and `test/csv/level1.csv`, `level2.csv` from https://tinyurl.com/wtq26.
- [ ] Check: 10 bills, level1 has 10 rows, level2 has 120 rows (12 questions each). Read the 12 questions once.
- [ ] Run the pipeline:
  ```
  python main.py --bills test/bills --level1-template test/csv/level1.csv --level2-template test/csv/level2.csv --out output/
  ```
- [ ] Watch logs for fallbacks / rate-limit warnings. Check `run_report.json`.

## Done when
`output/level1.csv` and `output/level2.csv` exist with correct row counts and no empty cells.

## If stuck
Rate limit -> lower workers or switch model via `.env`. One bill failed -> rerun with `--only BILL_ID`.
