"""Tests for refactor validation helpers."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.coverage_diff import load_percent, main as coverage_main
from scripts.refactor_tools import RefactorValidator


def test_load_percent_reads_pytest_cov_json(tmp_path: Path) -> None:
    report = tmp_path / "coverage.json"
    report.write_text(json.dumps({"totals": {"percent_covered": 97.25}}))

    assert load_percent(report) == 97.25


def test_refactor_validator_checks_minimum_coverage(tmp_path: Path) -> None:
    report = tmp_path / "coverage.json"
    report.write_text(json.dumps({"totals": {"percent_covered": 96.0}}))
    validator = RefactorValidator(minimum_coverage=95.0)

    assert validator.validate_coverage(report) == (True, 96.0)


def test_refactor_validator_summarizes_paths(tmp_path: Path) -> None:
    existing = tmp_path / "exists.txt"
    existing.write_text("ok")
    missing = tmp_path / "missing.txt"
    validator = RefactorValidator()

    assert validator.summarize_paths(existing, missing) == {
        str(existing): True,
        str(missing): False,
    }


def test_coverage_main_fails_when_below_minimum(tmp_path: Path, monkeypatch) -> None:
    report = tmp_path / "coverage.json"
    report.write_text(json.dumps({"totals": {"percent_covered": 90.0}}))
    monkeypatch.setattr(
        "sys.argv",
        ["coverage_diff.py", str(report), "--minimum", "95"],
    )

    assert coverage_main() == 1
