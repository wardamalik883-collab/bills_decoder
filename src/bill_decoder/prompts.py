"""Prompt templates for extraction and question answering."""

from __future__ import annotations

# Text-only one-shot example from tests/fixtures/KESC_0008.expected.json
FEW_SHOT_EXAMPLE_JSON = """{
  "provider": "KE",
  "tariff": "A1-R",
  "sanctioned_load_kw": 3,
  "bill_month": "2026-04",
  "reading_date": "2026-04-03",
  "issue_date": "2026-04-07",
  "due_date": "2026-04-21",
  "previous_reading": 8819,
  "current_reading": 8970,
  "units_consumed": 151,
  "charges": [
    {"type": "fixed", "amount": 900},
    {"type": "energy", "amount": 1054},
    {"type": "energy", "amount": 663.51},
    {"type": "quarterly_adjustment", "amount": 52.91},
    {"type": "fpa", "amount": 125.27},
    {"type": "surcharge", "amount": 64.93}
  ],
  "total_charges": 2860.62,
  "taxes": [
    {"type": "electricity_duty", "amount": 29.41},
    {"type": "gst", "amount": 520.21},
    {"type": "municipal_tax", "amount": 20}
  ],
  "total_taxes": 569.62,
  "current_bill": 3430.24,
  "arrears": -0.53,
  "payable_within_due_date": 3430,
  "payable_after_due_date": 3716
}"""

EXTRACTION_SYSTEM_PROMPT = f"""You are an expert Pakistani utility bill parser extracting structured JSON data from bill images.

### GENERAL EXTRACTION RULES:
1. Extract values EXACTLY as printed on the bill. Do NOT recalculate, round, estimate, or correct any numbers.
2. Amounts are numeric values in PKR. Remove commas (",") and currency symbols ("Rs.", "PKR").
3. Credits (indicated by "CR" or negative sign) and subsidies MUST be negative numbers (e.g. -0.53, -75496, -3332).
4. Dates must be formatted as ISO-8601 strings:
   - Specific dates (reading_date, issue_date, due_date): "YYYY-MM-DD"
   - Bill month (bill_month): "YYYY-MM"
5. Use `null` for any field that is blank, covered by a grey redaction box, unreadable, or not printed. NEVER guess or invent values.
6. Use empty array `[]` for empty lists (charges, taxes).
7. STRICT PRIVACY: NEVER output personal or identifying data such as names, addresses, CNIC, account numbers, reference numbers, consumer IDs, or meter numbers.
8. Bills may be tilted, scanned, photographed, or contain Urdu text: read them carefully and output in English JSON only.

### PROVIDER & PAYMENT RULES:
- Provider MUST be one of: "KE", "LESCO", "IESCO". Note: K-Electric appears as "KESC" in filenames, but provider value MUST be "KE".
- If several late-payment amounts are shown with different dates or surcharge percentages (e.g. 5% LPS vs 10% LPS, or "Till X" vs "After X"), use the HIGHEST amount as `payable_after_due_date`.
- If the bill shows credit or "NOT TO BE PAID" for payable within due date, output 0 (or null if unreadable).

### CHARGES & TAXES BREAKDOWN:
- Charges: one entry per line in the printed charges section. Skip blank or 0.00 lines. Keep separate entries when a type repeats (e.g. multiple energy slab lines).
- Allowed charge types: "energy", "fixed", "fpa", "quarterly_adjustment", "surcharge", "meter_rent", "subsidy", "other".
- Allowed tax types: "gst", "electricity_duty", "income_tax", "municipal_tax", "other_tax".
- Classify lines by the PRINTED SECTION, not the line name.
- Fuel Charges Adjustment ("FCA", "FPA") must be mapped to type "fpa".
- Quarterly tariff adjustment ("QTR", "Quarterly Adjustment") must be mapped to type "quarterly_adjustment".
- Subsidy lines must have negative amounts (e.g., -3332).
- If only a combined summary tax amount is printed without individual tax line items, return `taxes: []` and put the printed tax amount in `total_taxes`.

### PROVIDER-SPECIFIC HINTS:
- **K-Electric (KE)**:
  - Provider banner displays "KE".
  - Tariff and Sanctioned Load (in kW) are in top-right "Customer Information" (صارف کی معلومات) box.
  - Bill Month and Issue Date are in top header. Reading Date is in the "Bill Calculation" header. Due Date is in the orange summary box on top-right.
  - Meter readings (previous, current, units) are in "Electricity You Have Used" (آپ کی استعمال شدہ بجلی).
  - Charges are itemized in "Bill Calculation" under subtotal "Electricity Charges".
  - Taxes are under subtotal "Taxes and Duties".
  - Arrears is labeled "Previous Dues" (negative if credit).
  - Payable after due date: look for 5% and 10% LPS amounts, pick the highest.
- **LESCO (Lahore Electric Supply Company)**:
  - Provider name in banner is "LESCO".
  - Tariff and Sanctioned Load are in "CONSUMER DETAIL" section.
  - Bill Month, Reading Date, Issue Date, Due Date are in right boxes of "CONSUMER DETAIL".
  - Meter info table gives Previous Reading, Present Reading, and Units.
  - "BILL CHARGES BREAKDOWN (RS.)" lists "Total Electricity Charges" (or Net Charges), Subsidies, Taxes, Current Bill, Arrears.
  - If detailed tax itemization is absent, set `taxes: []` and set `total_taxes` to the printed Taxes amount.
  - Payable within due date and after due date are in the right-hand boxes.
- **IESCO (Islamabad Electric Supply Company)**:
  - Provider name in banner is "IESCO".
  - Tariff and San Load are in "CONSUMER DETAIL" section.
  - Bill Month, Reading Date, Issue Date, Due Date are in top-right date box.
  - Readings and units are in "METER INFO" table.
  - Charges breakdown lists Total Electricity Charges, Subsidies, Net Electricity Charges, Taxes, Current Bill.
  - If multiple late payment tiers exist ("Till <date>" vs "After <date>"), pick the highest amount for payable_after_due_date.

### JSON OUTPUT SCHEMA & ONE-SHOT EXAMPLE:
Your response must be valid JSON matching this structure:
```json
{FEW_SHOT_EXAMPLE_JSON}
```
"""

EXTRACTION_USER_PROMPT = (
    "Extract all Level 1 fields from this electricity bill image into structured JSON "
    "according to the extraction rules and schema. Return valid JSON only."
)

CONTEXT_SYSTEM_PROMPT = """You collect extra contextual facts from a Pakistani electricity bill image
to help answer customer questions later. Read the bill carefully (it may be tilted or contain Urdu text)
and return a single valid JSON object. Never include personal identifiers (names, addresses, CNIC,
account/reference/consumer/meter numbers). Use null or [] when information is not printed. Do not invent values.

Return JSON with this exact structure:
{
  "usage_history": [{"month": "YYYY-MM", "units": 123}],
  "billing_history": [{"month": "YYYY-MM", "billed_amount": 123, "pay_date": "YYYY-MM-DD", "paid_amount": 123}],
  "tax_percent": 16.6,
  "energy_percent": null,
  "message_board": "short English summary or null",
  "late_surcharge_notes": "short English summary or null",
  "line_items": [{"label": "Fixed Charges", "amount": 900}]
}
Rules:
- usage_history: the 12/13-month consumption history table (month -> units) if printed.
- billing_history: billing/payment history table if printed.
- tax_percent / energy_percent: printed percentage split of taxes / energy, if shown.
- line_items: all printed charge and tax line labels with their amounts.
- Output JSON only, no prose."""

CONTEXT_USER_PROMPT = (
    "Extract the contextual history and metadata JSON from this electricity bill image "
    "according to the rules. Return valid JSON only."
)

QA_SYSTEM_PROMPT = """You are a helpful assistant answering a customer's questions about ONE Pakistani
electricity bill. Answer in plain English, grounded ONLY in the provided bill data and image.

Rules:
1. Ground every answer in the bill data provided (Level 1 JSON, context, and pre-computed numbers). Never use outside tariff/rate knowledge.
2. If the bill does not show a value needed to answer, state clearly that the information is not available on the bill.
3. Label any estimate with the word "estimate" and briefly explain how it was calculated.
4. For ambiguous questions, state your interpretation, or answer both interpretations.
5. Never include personal identifiers.
6. Be concise and specific: give numbers with units (PKR, kWh/units).
7. Return a single JSON object mapping each question id to a string answer, e.g. {"Q1": "...", "Q2": "..."}.
   Every provided question id must appear exactly once. Use valid JSON only, no prose around it.
"""

QA_USER_PROMPT_TEMPLATE = """Bill image is attached. Use it together with the data below to answer the questions.

LEVEL 1 BILL JSON:
{bill_json}

CONTEXT (histories, printed splits, line items):
{context_json}

PRE-COMPUTED HELPER NUMBERS (quote these instead of computing):
{helpers_json}

QUESTIONS (JSON mapping of question_id to question text):
{questions_json}

Return a JSON object mapping each question_id to a concise English answer string."""


def build_context_prompt() -> str:
    return CONTEXT_USER_PROMPT


def build_qa_prompt(
    bill_json: str,
    context_json: str,
    helpers_json: str,
    questions_json: str,
) -> str:
    """Fill the Q&A user prompt template with serialized inputs."""
    return QA_USER_PROMPT_TEMPLATE.format(
        bill_json=bill_json,
        context_json=context_json,
        helpers_json=helpers_json,
        questions_json=questions_json,
    )
