# T10 - CSV I/O
**Phase D | ~10 min | Depends on: T02**

## Goal
Read the supplied templates and write completed CSVs with exact formatting.

## Steps
- [ ] `csv_io.py`: read `level1.csv` (`bill_id,json`) and `level2.csv` (`bill_id,question_id,question,answer`) with `csv.DictReader`, UTF-8.
- [ ] Preserve column names and **row order**; never change `bill_id`, `question_id`, `question`.
- [ ] Write with `csv.writer` / `DictWriter` (`QUOTE_MINIMAL`); JSON dumped with `json.dumps(obj, ensure_ascii=False, separators=(",", ":"))` on one line.
- [ ] Map `bill_id` -> image file in `bills/` by trying `.png`, `.jpg`, `.jpeg`.
- [ ] Round-trip test: write then read back; JSON parses; row counts equal template.
- [ ] Create sample templates for training bills (see T12) to test.

## Deliverable
`csv_io.py` + test.

## Done when
Output CSV opens correctly in Excel/LibreOffice and re-parses to the same objects.
