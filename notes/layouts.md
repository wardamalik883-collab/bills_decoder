# Utility Bill Layout Analysis & Provider Quirks

This document summarizes the layout structures, field locations, naming variants, and provider quirks across Pakistani utility bills (K-Electric, LESCO, IESCO) based on the training bills in `data/train/bills/`.

---

## 1. K-Electric (KE)

### Bills Analyzed
- `KESC_0008.png` (Standard residential)
- `KESC_0004.png` (Net metering / TOU residential)

### Key Field Locations & Label Variants
- **Provider**: Printed prominently in the top-left logo and banner as `KE`.
- **Tariff**:
  - Located in the top-right box labeled `Customer Information` / `صارف کی معلومات`.
  - Printed label: `Tariff`.
  - Typical values: `A1-R` (Residential).
- **Sanctioned Load**:
  - Located in the `Customer Information` box.
  - Printed label: `Sanc Load` (in kW).
  - Also displays `Conn Load` (Connected Load).
- **Bill Month**:
  - Located in the top header below the logo.
  - Printed label: `Bill Month: <Mon-YY>` (e.g., `Apr-26`, `Jun-26`). Standardized to `YYYY-MM`.
- **Issue Date**:
  - Located in the top header next to Bill Month.
  - Printed label: `Issue Date: <DD-Mon-YYYY>` (e.g., `07-Apr-2026`, `29-Jun-2026`). Standardized to `YYYY-MM-DD`.
- **Reading Date**:
  - Located in the header row of the `Bill Calculation` / `آپ کے موجودہ بل کا حساب` section on the right.
  - Printed label: `Reading Date: <DD-Mon-YY>` (e.g., `03-Apr-26`, `25-Jun-26`). Standardized to `YYYY-MM-DD`.
- **Due Date**:
  - Located in the top-right orange summary box labeled `Due Date` / `مقررہ تاریخ` and repeated in the payment stub at the bottom.
  - Printed label: `Due Date` (e.g., `21st Apr 2026`, `13th Jul 2026`). Standardized to `YYYY-MM-DD`.
- **Previous & Current Readings, Units Consumed**:
  - Located in the middle-left box labeled `Electricity You Have Used` / `آپ کی استعمال شدہ بجلی`.
  - Columns: `Previous Reading`, `Current Reading`, `Units (KWh)`, `MDI (KW)`.
  - In single-phase bills (`KESC_0008`), single row: `Energy`.
  - In TOU / Net-Metering bills (`KESC_0004`), multiple rows: `Energy - Off Peak`, `Energy - Peak`, `Import Energy Off Peak`, `Import Energy Peak`.
  - Total consumed units are highlighted in the top summary card `Current Month` / `موجودہ مہینہ` (e.g., `151 units = Rs.3,430.24`, `901 units = Rs.45,570.25`).

### Charges Section
- **Printed Section Name**:
  - Table is titled `Bill Calculation` / `آپ کے موجودہ بل کا حساب`.
  - The charges block has subtotal line `Electricity Charges`.
- **Lines in Charges Section**:
  - `Fixed Charges` -> mapped to `"fixed"`
  - `Variable Upto 100 Units (Protected)` / `Variable Upto 200 Units (Protected)` / `Variable Off Peak` / `Variable Peak` -> mapped to `"energy"`
  - `Uniform Quarterly Adjustment` (can be positive or negative) -> mapped to `"quarterly_adjustment"`
  - `FCA :<Month-YY>` (Fuel Charges Adjustment) -> mapped to `"fpa"`
  - `Additional Surcharge (PHL)` -> mapped to `"surcharge"`
- **Total Charges**:
  - Printed line: `Electricity Charges` (e.g., `2,860.62`, `38,098.01`).

### Tax / Government Section
- **Printed Section Name**:
  - Under `Bill Calculation`, immediately below `Electricity Charges`, with subtotal line `Taxes and Duties`.
- **Lines in Tax Section**:
  - `Electricity Duty` -> mapped to `"electricity_duty"`
  - `Sales Tax u/s 3(1)*` -> mapped to `"gst"`
  - `MUCT (KMC)` (Municipal Utility Charges & Taxes) -> mapped to `"municipal_tax"`
- **Total Taxes**:
  - Printed line: `Taxes and Duties` (e.g., `569.62`, `7,472.24`).

### Billing & Payable Amounts
- **Current Bill**:
  - Printed line: `Electricity Charges for current month` (e.g., `3,430.24`, `45,570.25`).
- **Arrears**:
  - Printed line in `Bill Calculation`: `Previous Dues` (e.g., `-0.53`, `-91,877.02`).
  - Also displayed in top summary box: `Previous Dues` / `گزشتہ بقایا جات`.
- **Payable Within Due Date**:
  - Printed line: `Amount Payable within Due Date` (e.g., `3,430`, `0`).
  - Also in top-left summary card: `Amount Due` / `واجب الادا رقم`.
- **Payable After Due Date**:
  - Printed at the bottom of `Bill Calculation` with late payment surcharge (LPS).
  - In KE bills, two late dates are printed: 5% LPS and 10% LPS (e.g., `Amount Payable from 22-Apr - 24-Apr with 5% LPS: 3,574`, `Amount Payable after 24-Apr-26 with 10% LPS: 3,716`).
  - **Rule**: `payable_after_due_date` is the **highest** late payment amount (e.g., `3716`). If payable within due date is 0 (as in Net Metering `KESC_0004`), it is `0`.

### Urdu, Tilt, and Redaction
- **Urdu Content**:
  - Section headers have parallel Urdu translations (e.g., `Customer Information` / `صارف کی معلومات`, `Bill Calculation` / `آپ کے موجودہ بل کا حساب`, `Electricity You Have Used` / `آپ کی استعمال شدہ بجلی`).
  - Footer notes and disclaimer in Urdu.
- **Orientation**: Straight digital scan / export, not tilted.
- **Redacted (Grey Boxes)**:
  - Top-center barcode/QR scan area.
  - `Contract No`, `Security Deposit`, `Invoice No`, `Dispatch ID`.
  - `User Name`, `Tenant CNIC/NTN/STRN`, `Consumer No`, `Meter No`.
  - Bottom payment slip consumer details.

### History Sections (Level 2 Q&A)
- **13 Month Usage History**:
  - Middle-left card titled `13 Month Usage History` / `13 مہینے کے استعمال کی تفصیل`.
  - Vertical bar chart spanning previous 12 months up to current month, with exact numeric unit values on each bar and months on the x-axis.
- **Billing & Payment History**:
  - Card titled `Billing & Payment History` / `بلنگ اور ادائیگی کی تفصیل`.
  - Columns: `MM / YY`, `Billed Amount`, `Pay-Date`, `Payment`.
- **Message Board**:
  - Box titled `Message Board` / `میسج بورڈ` containing announcements regarding FCA, XWDISCOs, Net Metering regulations, etc.

---

## 2. LESCO (Lahore Electric Supply Company)

### Bills Analyzed
- `LESCO_0005.png` (Net metering / Domestic connection)
- `LESCO_0006.png` (Commercial connection)

### Key Field Locations & Label Variants
- **Provider**: Printed in top header banner as `LESCO LAHORE ELECTRIC SUPPLY COMPANY`.
- **Tariff**:
  - Located in `CONSUMER DETAIL` section.
  - Label variants: `TARIFF`, `TARIFF CATEGORY` / `نرخ قسم`.
  - Typical values: `A-1b(03)T`, `A-2a(04)`.
- **Sanctioned Load**:
  - Located in `CONSUMER DETAIL` section.
  - Label variants: `SAN LOAD`, `SAN. LOAD`, `San Load` / `لوڈ`.
- **Bill Month**:
  - Located in the right sub-box of `CONSUMER DETAIL`.
  - Printed label: `BILL MONTH` / `مہینہ بل` (e.g., `JUL 2026`, `AUG 2026`). Standardized to `YYYY-MM`.
- **Issue Date**:
  - Located in the date block on the right of `CONSUMER DETAIL`.
  - Printed label: `ISSUE DATE` / `تاریخ اجراء` (e.g., `20 JUL 26`, `29 AUG 26`). Standardized to `YYYY-MM-DD`.
- **Reading Date**:
  - Located to the left of Issue Date.
  - Printed label: `READING DATE` / `تاریخ ریڈنگ` (e.g., `17 JUL 26`, `26 AUG 26`). Standardized to `YYYY-MM-DD`.
- **Due Date**:
  - Located with a warning icon on the right side.
  - Printed label: `DUE DATE` / `مقررہ تاریخ` (e.g., `30 JUL 26`, `09 SEP 26`). Standardized to `YYYY-MM-DD`.
- **Previous & Current Readings, Units Consumed**:
  - Located in `METER INFO` box.
  - Columns: `MF` (Multiplying Factor), `PREVIOUS READING` / `سابقہ ریڈنگ`, `PRESENT READING` / `موجودہ ریڈنگ`, `UNITS` / `یونٹ`.
  - Single-phase meter (`LESCO_0006`): single line with previous reading (`22238`), present reading (`22303`), units (`65`).
  - Net metering TOU (`LESCO_0005`): multiple rows for peak/off-peak and export/import.

### Charges & Taxes Section
- **Printed Section Name**:
  - Titled `BILL CHARGES BREAKDOWN (RS.)`.
- **Lines in Section**:
  - Left column:
    - `Total Electricity Charges` / `کل چارجز`
    - `Subsidies` / `رعایت`
    - `Net Electricity Charges` / `نیٹ چارجز`
    - `Taxes` / `قابل ادا ٹیکس`
    - `Current Bill` / `موجودہ بل`
    - `Grand Total` / `کل واجبات`
  - Right column:
    - `Arrears` / `بقایا جات`
    - `Installment` / `قسط`
    - `Adjustments` / `تصحیح بل`
- **Mapping**:
  - `total_charges`: `Total Electricity Charges` or `Net Electricity Charges` (e.g., `17367.77`, `3777.49`).
  - `total_taxes`: `Taxes` line (e.g., `3358.23`, `1723.51`).
  - In DISCOs without granular itemization in this breakdown table, itemized lines may be derived or set to the section totals.

### Billing & Payable Amounts
- **Current Bill**: `Current Bill` / `موجودہ بل` (e.g., `20726`, `5501`).
- **Arrears**: `Arrears` / `بقایا جات` (e.g., `-75496`, `39411`). Note: negative values represent credit.
- **Payable Within Due Date**:
  - Right card titled `PAYABLE WITHIN DUE DATE` / `مقررہ تاریخ تک واجب الادا`.
  - In `LESCO_0006`: `44912`.
  - In `LESCO_0005`: `54770CR` (Credit; not to be paid).
- **Payable After Due Date**:
  - Right card titled `PAYABLE AFTER DUE DATE` / `مقررہ تاریخ کے بعد واجب الادا`.
  - Split across payment windows: e.g., `Upto 14/09/26: 45088`, `After 14/09/26: 45263`.
  - **Rule**: Pick the **highest** amount (`45263`). If credit / `NOT TO BE PAID`, value is `0` or `null`.

### Urdu, Tilt, and Redaction
- **Urdu Content**: Extensive dual English/Urdu labels for every header and field.
- **Orientation**:
  - `LESCO_0005.png`: Slight physical photograph perspective.
  - `LESCO_0006.png`: Slightly photographed / wavy paper.
- **Redacted (Grey Boxes)**:
  - Reference number, Consumer ID, Name & Address, Transformer, Feeder, Sub Division.
  - QR code box on the right.

### History Sections (Level 2 Q&A)
- **Bill History**:
  - Located at bottom-left in table titled `BILL HISTORY`.
  - 12 months split into two 6-month columns:
    - `MONTH`, `STATUS`, `UNITS`, `BILL (RS.)`, `PAYMENT (RS.)`.

---

## 3. IESCO (Islamabad Electric Supply Company)

### Bills Analyzed
- `IESCO_0004.jpg` (Residential protected)

### Key Field Locations & Label Variants
- **Provider**: Printed in top banner as `IESCO ISLAMABAD ELECTRIC SUPPLY COMPANY`.
- **Tariff**:
  - Located in `CONSUMER DETAIL` section.
  - Printed label: `TARIFF` (e.g., `A-1A(01)`).
  - Also displays `TARIFF CATEGORY` (e.g., `Domestic`) and `CATEGORY` (e.g., `Protected`).
- **Sanctioned Load**:
  - Located in `CONSUMER DETAIL`.
  - Printed label: `SAN LOAD` (e.g., `3`).
- **Bill Month**:
  - Located in top-right date box.
  - Printed label: `BILL MONTH` / `مہینہ بل` (e.g., `SEP 26`). Standardized to `YYYY-MM` (`2026-09`).
- **Issue Date**:
  - Printed label: `ISSUE DATE` / `تاریخ اجراء` (e.g., `26 SEP 26`). Standardized to `YYYY-MM-DD` (`2026-09-26`).
- **Reading Date**:
  - Printed label: `READING DATE` / `تاریخ ریڈنگ` (e.g., `25 SEP 26`). Standardized to `YYYY-MM-DD` (`2026-09-25`).
- **Due Date**:
  - Located below date box with triangle alert icon.
  - Printed label: `DUE DATE` / `مقررہ تاریخ` (e.g., `08 OCT 26`). Standardized to `YYYY-MM-DD` (`2026-10-08`).
- **Previous & Current Readings, Units Consumed**:
  - Located in `METER INFO` box.
  - Columns: `MF`, `PREVIOUS READING` (`9301`), `PRESENT READING` (`9459`), `UNITS` (`158`).

### Charges & Taxes Section
- **Printed Section Name**:
  - Titled `BILL CHARGES BREAKDOWN (RS.)`.
- **Lines in Section**:
  - `Total Electricity Charges`: `6102`
  - `Subsidies`: `3332`
  - `Net Electricity Charges 84.76 %`: `2770`
  - `Taxes 15.24 %`: `498`
  - `Current Bill`: `3267`
  - `Arrears`: `0`
  - `Installment`: `0`
  - `Adjustments`: `0`
  - `Total FPA`: `267`
  - `Grand Total`: `3535`
- **Mapping**:
  - `total_charges`: `Total Electricity Charges` (`6102`) or Net Charges (`2770`).
  - `total_taxes`: `Taxes` (`498`).

### Billing & Payable Amounts
- **Current Bill**: `3267`.
- **Arrears**: `0`.
- **Payable Within Due Date**:
  - Right box `PAYABLE WITHIN DUE DATE`: `3535`.
- **Payable After Due Date**:
  - Right box `PAYABLE AFTER DUE DATE`:
    - `Till 12-OCT-26: 3,674` (L.P Surcharge: 139)
    - `After 12-OCT-26: 3,812` (L.P Surcharge: 277)
  - **Rule**: Highest late payment amount is `3812`.

### Urdu, Tilt, and Redaction
- **Urdu Content**:
  - Prominent Urdu alert box explaining Fuel Price Adjustment (FPA) and Government subsidy:
    `آپ کے اس بل میں جولائی 26 کے صرف شدہ یونٹس 110 کے ایندھن کی قیمت (FPA) کے 267 روپے بھی شامل ہیں`
    `آپ کے موجودہ بجلی کے بل 6,599 روپے میں حکومت پاکستان کی جانب سے 3,332 روپے کی سبسڈی شامل ہے`
- **Orientation**: Upright digital layout.
- **Redacted (Grey Boxes)**:
  - Top-right 1Link code, Consumer Reference/ID, Name & Address, Transformer, Feeder, Sub Division, Meter image barcode, QR code.

### History Sections (Level 2 Q&A)
- **Bill History**:
  - Table titled `BILL HISTORY` with 12 months (Sep 25 through Aug 26).
  - Columns: `MONTH`, `STATUS`, `UNITS`, `BILL (RS.)`, `PAYMENT (RS.)`.
- **Bottom Payment Slip**:
  - Repeated copy of Bill Month, Due Date, Payable Within Due Date, Payable After Due Date.

---

## 4. Key Rules & Decision Guidelines Across All Providers

1. **Credits and Subsidies**:
   - Any amount suffixed with `CR` or printed as credit/negative is negative (e.g., `-0.53`, `-91877.02`, `-75496`).
   - If a bill has a net credit balance (`NOT TO BE PAID`), `payable_within_due_date` is `0` (or `null` if unreadable).
2. **Payable After Due Date**:
   - When multiple post-due-date windows exist with varying late surcharges (5% vs 10%, or Tier 1 vs Tier 2), always pick the **highest** amount.
3. **Classification by Printed Section**:
   - Values are classified into `charges` vs `taxes` based on the printed section header (`Electricity Charges` vs `Taxes and Duties`), not by guessing item names.
4. **Dates Format**:
   - Always standardize to ISO-8601: `YYYY-MM-DD` for specific dates and `YYYY-MM` for bill months.
