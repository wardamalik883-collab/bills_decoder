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
