# Utility Bill Decoder

AI-powered extractor and Q&A assistant for Pakistani electricity utility bills (K-Electric, LESCO, IESCO).

## Setup

### Prerequisites
- Python 3.14.2 (tested; requires Python >= 3.11)
- Git

### Installation

On a fresh clone, run:

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
# source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install the bill_decoder package in editable mode
pip install -e .
```

### Environment Configuration

Create a `.env` file in the project root based on `.env.example`:

```bash
cp .env.example .env
```

Set the required environment variables in `.env`:
```env
MODEL_PROVIDER=google
MODEL_NAME=gemini-3.1-flash-lite
API_KEY=your-api-key-here
```

### Running Tests

```bash
pytest
```

## Usage

Run the full pipeline on a folder of bill images and the supplied CSV templates:

```bash
python main.py \
  --bills test/bills \
  --level1-template test/csv/level1.csv \
  --level2-template test/csv/level2.csv \
  --out output/
```

On Windows PowerShell (single line):

```powershell
python main.py --bills test/bills --level1-template test/csv/level1.csv --level2-template test/csv/level2.csv --out output/
```

Optional flags:
- `--workers N` concurrent workers (default 2)
- `--only BILL_ID` process a single bill
- `--no-cache` clear and ignore the LLM cache

Outputs written to `--out`:
- `level1.csv` - one row per bill with a compact single-line JSON object
- `level2.csv` - one row per (bill, question) with an English answer
- `run_report.json` - timings, row counts, and any bills that fell back

## Architecture

```
bills/*.png|jpg
   |
   v
[preprocess]  (EXIF rotation fix, RGB, downscale)
   |
   v
[Extractor: vision LLM + strict JSON schema]  --> raw Level-1 JSON
   |
   v
[Validator (code)]  readings/sums/dates/signs
   |   \__ on warnings: retry LLM once with the error message
   v
Level-1 JSON  --------------------------> level1.csv
   |
   v
[Context extractor: usage history, billing history, tax split, line items]
   |
   v
[Q&A: LLM + calc tools (Python)]  --> answers (English, estimates labelled)
   |
   v
level2.csv
```

## Design choices

- **Vision LLM first** (not OCR): handles tilted, low-quality and Urdu bills.
- **Provider abstraction**: switch between google / anthropic / openai via `MODEL_PROVIDER` and `MODEL_NAME`.
- **Strict schema**: Pydantic models validate Level 1 output; unknown keys are dropped.
- **Math in code**: percentages, averages, counts, differences are computed in Python (`calc_tools.py`) and passed to the LLM as facts.
- **Caching**: every LLM response is cached on disk (`cache/`) keyed by a SHA-256 hash; reruns cost nothing.
- **Fewer requests**: all 12 questions per bill are asked in one call (fallback to per-question).
- **Fail-soft**: any bill failure yields `null` fields / "not available" answers; the run never aborts.

## Packaging

Build the submission ZIP (verified `<= 15 MB`, no secrets):

```bash
python scripts/package.py
```

## AI usage

- **Models/APIs used by the solution code**: Google Gemini (`gemini-3.1-flash-lite`) for vision extraction and Q&A, via the official `google-genai` SDK. The client also supports `claude-haiku-4-5` and `gpt-4.1-mini` / `gpt-5-mini` through the same abstraction. Only whitelisted competition models are accepted.
- **External invoice/OCR services**: none (no Azure prebuilt-invoice, Textract, Mindee). No local OCR is used; extraction is done directly by the vision LLM.
- **AI tools used to write the code**: opencode (AI coding assistant).

## Known limitations

- Accuracy depends on image quality; heavily blurred or covered fields are returned as `null` (a correct null is preferred over a guess).
- Usage-history questions require the bill's history table to be printed; otherwise the answer states that it is not available.
- Generated CSVs are always produced by code; they are never hand-edited.
