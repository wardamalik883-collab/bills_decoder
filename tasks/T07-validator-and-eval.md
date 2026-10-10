# T07 - Validator, retry and evaluation
**Phase B | ~25 min | Depends on: T06**

## Goal
Catch obvious extraction mistakes automatically and measure accuracy.

## Steps
- [ ] `validator.py` sanity checks (warnings that trigger a retry, not hard failures):
  - `current_reading - previous_reading` is close to `units_consumed`
  - `sum(charges)` is close to `total_charges` (when printed)
  - `sum(taxes)` is close to `total_taxes` (when printed)
  - `payable_after_due_date >= payable_within_due_date`
  - dates match `YYYY-MM-DD`; `bill_month` matches `YYYY-MM`; due date is after issue date
  - subsidy amounts are negative; no identifier-like strings in output
- [ ] If a check fails: re-ask the model once with a specific message ("charges sum to X but printed total is Y; re-read the charges section"). Keep original values if the retry is no better. Remember: **extract as printed, do not "fix" bill amounts to make them add up.**
- [ ] `eval_level1.py`: compare output to expected JSON field by field (text/dates exact, numbers within +-1) and print a score table.
- [ ] Run on all 5 training bills; fix prompt issues one by one.

## Deliverable
`validator.py`, evaluation script, notes on remaining errors.

## Done when
KESC_0008 matches expected JSON (all fields), and the other 4 bills show no obviously wrong values.

## If stuck
Look at which field fails most, add a targeted instruction plus a hint to the prompt. Avoid giant prompts; precise rules work better.
