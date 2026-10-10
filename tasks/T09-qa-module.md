# T09 - Q&A module
**Phase C | ~20 min | Depends on: T08**

## Goal
Answer any customer question about a bill: correct, grounded, clear.

## Steps
- [ ] `qa.py`: `answer_questions(bill_json, context, image_path, questions) -> dict[question_id, str]`.
- [ ] Approach: one call per bill containing all 12 questions to save requests (fallback to per-question call if parsing fails).
- [ ] Give the LLM: Level 1 JSON, extracted context, the image, and **pre-computed helper numbers** (tax %, avg usage, etc. from `calc_tools`) so it quotes rather than computes.
- [ ] System prompt rules (guide 6.1):
  - ground answers only in the bill; no outside tariff/rate info
  - if the bill does not show a needed value, say so clearly
  - label estimates ("estimate") and explain the calculation
  - for ambiguous questions state the interpretation, or answer both
  - no personal identifiers; English only, even if bill is Urdu
  - concise, specific, with numbers and units (PKR)
- [ ] Output JSON `{ "Q1": "...", ... }`; validate every id exists; any missing answer gets a safe fallback sentence (never empty).
- [ ] Test with guide 6.2 samples ("How much of my bill is taxes?", "How many months went above 200 units?") against KESC_0008.

## Deliverable
`qa.py`.

## Done when
Sample answers on KESC_0008 are numerically correct and mention the interpretation when relevant.

## Tip
Questions are unknown until 12:30. Test with a varied set you write yourself: totals, comparisons, averages, "why is my bill high", "what if I use 50 more units" (estimate, with stated assumptions), "when is it due", "what happens if I pay late".
