# T11 - Pipeline CLI and error handling
**Phase D | ~15 min | Depends on: T06, T09, T10**

## Goal
One command produces both CSVs reliably.

## Steps
- [ ] `pipeline.py`: for each bill_id in template -> extract L1 -> context -> Q&A.
- [ ] `main.py` CLI with argparse: `--bills`, `--level1-template`, `--level2-template`, `--out`, optional `--workers` (default 2), `--only BILL_ID`, `--no-cache`.
- [ ] Per-bill try/except: on failure log and use safe fallback (L1 with nulls; L2 answers "This information could not be determined from the bill image."). Run never aborts.
- [ ] Progress logging (`[3/10] KESC_0002 ... ok`), a final summary (successes, fallbacks, time).
- [ ] Write a `run_report.json` listing any bill that fell back, for quick review.
- [ ] Final assertions: row counts (10 and 120), no empty json/answer cell, JSON schema-valid.

## Deliverable
`pipeline.py`, `main.py`.

## Done when
Command runs start-to-finish on the training bills, even if you deliberately break one image.
