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
