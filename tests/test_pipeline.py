"""Tests for the end-to-end pipeline using a mocked LLM client."""

import csv
import json
from pathlib import Path

from PIL import Image

from bill_decoder import pipeline
from bill_decoder.config import Config

BILL_JSON = {
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
    "charges": [{"type": "fixed", "amount": 900}, {"type": "energy", "amount": 1054}],
    "total_charges": 1954,
    "taxes": [{"type": "gst", "amount": 520.21}],
    "total_taxes": 520.21,
    "current_bill": 3430.24,
    "arrears": -0.53,
    "payable_within_due_date": 3430,
    "payable_after_due_date": 3716,
}

CONTEXT_JSON = {
    "usage_history": [{"month": "2026-03", "units": 210}, {"month": "2026-02", "units": 150}],
    "billing_history": [],
    "tax_percent": 16.6,
}


class FakeClient:
    def __init__(self, config=None):
        self.config = config

    def generate(self, prompt, image_path=None, system=None, json_mode=True, no_cache=False):
        sys_lower = (system or "").lower()
        if "contextual facts" in sys_lower:
            return json.dumps(CONTEXT_JSON)
        if "answering" in sys_lower:
            data = json.loads(prompt.split("QUESTIONS (JSON mapping of question_id to question text):")[1].split("\n")[0])
            return json.dumps({qid: f"Answer for {qid}" for qid in data})
        return json.dumps(BILL_JSON)


def _make_image(path: Path) -> None:
    Image.new("RGB", (50, 50), "white").save(path)


def test_pipeline_end_to_end(tmp_path: Path, monkeypatch) -> None:
    bills = tmp_path / "bills"
    bills.mkdir()
    _make_image(bills / "KESC_0008.png")

    l1 = tmp_path / "level1.csv"
    l1.write_text("bill_id,json\nKESC_0008,\n", encoding="utf-8")

    l2 = tmp_path / "level2.csv"
    with open(l2, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["bill_id", "question_id", "question", "answer"])
        w.writerow(["KESC_0008", "Q1", "How much is the bill?", ""])
        w.writerow(["KESC_0008", "Q2", "When is it due?", ""])

    monkeypatch.setattr(pipeline, "LLMClient", FakeClient)
    config = Config(model_provider="google", model_name="gemini-3.1-flash-lite", api_key="x")

    report = pipeline.run_pipeline(
        bills_dir=bills,
        level1_template=l1,
        level2_template=l2,
        out_dir=tmp_path / "out",
        config=config,
        workers=1,
    )

    assert report["level1_rows"] == 1
    assert report["level2_rows"] == 2

    out1 = list(csv.DictReader(open(tmp_path / "out" / "level1.csv", encoding="utf-8")))
    assert json.loads(out1[0]["json"])["provider"] == "KE"

    out2 = list(csv.DictReader(open(tmp_path / "out" / "level2.csv", encoding="utf-8")))
    assert all(row["answer"].strip() for row in out2)
    assert report["fallbacks"] == 0


class RaisingClient:
    def __init__(self, config=None):
        self.config = config

    def generate(self, prompt, image_path=None, system=None, json_mode=True, no_cache=False):
        raise RuntimeError("model unavailable")


def test_pipeline_broken_image_falls_back(tmp_path: Path, monkeypatch) -> None:
    bills = tmp_path / "bills"
    bills.mkdir()
    (bills / "KESC_0008.png").write_bytes(b"not-an-image")

    l1 = tmp_path / "level1.csv"
    l1.write_text("bill_id,json\nKESC_0008,\n", encoding="utf-8")
    l2 = tmp_path / "level2.csv"
    l2.write_text("bill_id,question_id,question,answer\nKESC_0008,Q1,Q?, \n", encoding="utf-8")

    monkeypatch.setattr(pipeline, "LLMClient", RaisingClient)
    config = Config(model_provider="google", model_name="gemini-3.1-flash-lite", api_key="x")

    report = pipeline.run_pipeline(bills, l1, l2, tmp_path / "out", config, workers=1)

    assert report["fallbacks"] == 1
    out1 = list(csv.DictReader(open(tmp_path / "out" / "level1.csv", encoding="utf-8")))
    obj = json.loads(out1[0]["json"])
    assert all(obj[k] is None for k in ("provider", "tariff", "bill_month"))
    assert obj["charges"] == []
    out2 = list(csv.DictReader(open(tmp_path / "out" / "level2.csv", encoding="utf-8")))
    assert out2[0]["answer"].strip()
