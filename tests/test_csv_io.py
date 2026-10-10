"""Tests for CSV I/O round-trip and image lookup."""

from pathlib import Path

from bill_decoder.csv_io import (
    dump_json_line,
    find_image,
    read_level1_template,
    read_level2_template,
    write_level1_csv,
    write_level2_csv,
)


def test_level1_round_trip(tmp_path: Path) -> None:
    template = tmp_path / "level1.csv"
    template.write_text("bill_id,json\nKESC_0008,\n", encoding="utf-8")

    rows = read_level1_template(template)
    assert rows[0]["bill_id"] == "KESC_0008"

    rows[0]["json"] = dump_json_line({"provider": "KE", "note": "a,b"})
    out = tmp_path / "out1.csv"
    write_level1_csv(out, rows)

    reread = read_level1_template(out)
    assert reread == rows
    assert "," in reread[0]["json"]


def test_level2_round_trip(tmp_path: Path) -> None:
    template = tmp_path / "level2.csv"
    template.write_text(
        "bill_id,question_id,question,answer\nKESC_0008,Q1,How much?,42\n", encoding="utf-8"
    )
    rows = read_level2_template(template)
    assert rows[0]["question"] == "How much?"

    rows[0]["answer"] = "It is 42 PKR."
    out = tmp_path / "out2.csv"
    write_level2_csv(out, rows)
    assert read_level2_template(out) == rows


def test_find_image(tmp_path: Path) -> None:
    (tmp_path / "KESC_0008.jpg").write_bytes(b"x")
    assert find_image(tmp_path, "KESC_0008") == tmp_path / "KESC_0008.jpg"
    assert find_image(tmp_path, "MISSING") is None
