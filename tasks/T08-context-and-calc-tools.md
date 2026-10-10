# T08 - Context extraction and calc tools
**Phase C | ~15 min | Depends on: T06**

## Goal
Collect extra bill data needed for questions and make all math deterministic.

## Steps
- [ ] `context.py`: second extraction pass (or extended prompt) that returns extra facts, as printed:
  - 12/13-month usage history (month -> units)
  - billing and payment history (month, billed amount, pay date, paid amount)
  - printed energy/tax percentage split, if any
  - message board / notes text (English summary)
  - any printed late surcharge rates and amounts
  - all printed line items with labels (for explaining charges)
- [ ] Validate shape with pydantic; allow nulls.
- [ ] `calc_tools.py` pure Python functions with tests: `percentage(part, whole)`, `average(values)`, `count_above(values, threshold)`, `max_min_month(history)`, `difference(a, b)`, `cost_per_unit(total, units)`, `estimate_late_penalty(...)`, etc.
- [ ] Write `tests/test_calc_tools.py`.
- [ ] Verify with guide examples: taxes = 569.62 / 3430.24 = about 16.6%; history above 200 units for KESC_0008 = 2.

## Deliverable
`context.py`, `calc_tools.py`, passing tests.

## Done when
Context for KESC_0008 includes the 13-month history and `count_above(history, 200)` returns the guide's answer.
