# T03 - Study training bills and build ground truth
**Phase A | ~20 min | Depends on: T01**

## Goal
Understand the 3 provider layouts and create a test fixture so we can measure accuracy.

## Steps
- [ ] Open all 5 bills: `IESCO_0004.jpg`, `KESC_0004.png`, `KESC_0008.png`, `LESCO_0005.png`, `LESCO_0006.png`.
- [ ] For each provider note: where tariff, sanctioned load, dates, readings, charges section, tax section, arrears, payable amounts appear; label variants (Sanc Load / S.Load / San Load); Urdu parts; tilted?
- [ ] Save `tests/fixtures/KESC_0008.expected.json` from guide section 5.7 (exact copy).
- [ ] Hand-write expected JSON for 1-2 more bills (even partial) for comparison. Use `null` where grey box/unreadable. This is for your own testing only.
- [ ] Write a short `notes/layouts.md` listing quirks per provider (these become prompt hints).

## Deliverable
`KESC_0008.expected.json` plus layout notes.

## Done when
You can explain, for each provider, which printed section maps to `charges` vs `taxes`, and where `payable_after_due_date` comes from.

## Reminders (from the guide)
- Credits/subsidies are negative (`38209CR` -> `-38209`).
- Highest late-payment amount is `payable_after_due_date`.
- Skip charge lines that are blank or `0`.
- Classify by **section**, not by name.
