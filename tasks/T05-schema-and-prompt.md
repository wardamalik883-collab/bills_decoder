# T05 - Schema and extraction prompt
**Phase B | ~20 min | Depends on: T03**

## Goal
Define the exact Level 1 schema and a strong extraction prompt.

## Steps
- [ ] `schema.py` with pydantic models matching guide 5.1: provider (`KE|LESCO|IESCO`), tariff, sanctioned_load_kw, bill_month, reading_date, issue_date, due_date, readings, units_consumed, charges[], total_charges, taxes[], total_taxes, current_bill, arrears, payable_within_due_date, payable_after_due_date.
- [ ] Every field present; nullable where allowed; numbers are numbers; `[]` for empty lists.
- [ ] Enum for charge types (`energy, fixed, fpa, quarterly_adjustment, surcharge, meter_rent, subsidy, other`) and tax types (`gst, electricity_duty, income_tax, municipal_tax, other_tax`).
- [ ] `prompts.py`: system prompt including all rules from guide 5.2 - 5.4:
  - extract as printed, do not recalculate or round
  - strip commas and "Rs."; credits negative
  - date formats; `null` for unreadable/covered/not printed; no guessing
  - never output names, addresses, CNIC, account/consumer/meter numbers
  - classify by printed section; FPA and FCA -> `fpa`; subsidy negative
  - combined tax only -> `taxes: []` and put the value in `total_taxes`
  - K-Electric file prefix is KESC but provider value is `KE`
  - bill may be tilted or in Urdu; read it anyway
- [ ] Add the KESC_0008 input/output as a one-shot example (text of the JSON only, to save tokens).
- [ ] Add provider-specific hints from `notes/layouts.md`.

## Deliverable
`schema.py`, `prompts.py`.

## Done when
`Level1Bill.model_validate(expected_json)` passes for KESC_0008.
